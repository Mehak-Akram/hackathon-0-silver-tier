"""
Retry logic with exponential backoff for Gold Tier Autonomous AI Employee.

Provides configurable retry mechanisms using tenacity library with
exponential backoff, jitter, and integration with circuit breakers.
"""
from typing import Callable, Optional, Any, Type
from functools import wraps
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
    RetryError
)


logger = structlog.get_logger("retry_logic")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
        multiplier: float = 2.0,
        retry_exceptions: Optional[tuple] = None
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            min_wait: Minimum wait time in seconds
            max_wait: Maximum wait time in seconds
            multiplier: Exponential backoff multiplier
            retry_exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
        self.retry_exceptions = retry_exceptions or (Exception,)


# Default retry configurations for different operation types
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    min_wait=1.0,
    max_wait=10.0,
    multiplier=2.0
)

MCP_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    min_wait=2.0,
    max_wait=30.0,
    multiplier=2.0
)

EXTERNAL_API_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    min_wait=1.0,
    max_wait=60.0,
    multiplier=2.0
)

FILE_OPERATION_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    min_wait=0.5,
    max_wait=5.0,
    multiplier=1.5
)


def with_retry(
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
) -> Callable:
    """
    Decorator to add retry logic with exponential backoff.

    Args:
        config: Retry configuration (uses DEFAULT_RETRY_CONFIG if None)
        operation_name: Name for logging (uses function name if None)

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(config=MCP_RETRY_CONFIG, operation_name="mcp_call")
        async def call_mcp_api():
            # Your code here
            pass
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG

    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.multiplier,
                min=config.min_wait,
                max=config.max_wait
            ),
            retry=retry_if_exception_type(config.retry_exceptions),
            before_sleep=before_sleep_log(logger, structlog.INFO),
            after=after_log(logger, structlog.DEBUG)
        )
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                logger.debug(
                    "retry_attempt_start",
                    operation=op_name,
                    max_attempts=config.max_attempts
                )
                result = await func(*args, **kwargs)
                logger.debug(
                    "retry_attempt_success",
                    operation=op_name
                )
                return result
            except Exception as e:
                logger.warning(
                    "retry_attempt_failed",
                    operation=op_name,
                    error_type=type(e).__name__,
                    error=str(e)
                )
                raise

        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.multiplier,
                min=config.min_wait,
                max=config.max_wait
            ),
            retry=retry_if_exception_type(config.retry_exceptions),
            before_sleep=before_sleep_log(logger, structlog.INFO),
            after=after_log(logger, structlog.DEBUG)
        )
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                logger.debug(
                    "retry_attempt_start",
                    operation=op_name,
                    max_attempts=config.max_attempts
                )
                result = func(*args, **kwargs)
                logger.debug(
                    "retry_attempt_success",
                    operation=op_name
                )
                return result
            except Exception as e:
                logger.warning(
                    "retry_attempt_failed",
                    operation=op_name,
                    error_type=type(e).__name__,
                    error=str(e)
                )
                raise

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def retry_with_circuit_breaker(
    func: Callable,
    circuit_breaker: Any,
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with both retry logic and circuit breaker protection.

    The circuit breaker wraps the retry logic, so retries happen within
    a single circuit breaker call. If all retries fail, the circuit breaker
    records one failure.

    Args:
        func: Async function to execute
        circuit_breaker: Circuit breaker instance
        config: Retry configuration
        operation_name: Name for logging
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        RetryError: If all retry attempts fail
        CircuitBreakerError: If circuit is open

    Example:
        result = await retry_with_circuit_breaker(
            call_mcp_api,
            mcp_circuit_breaker,
            config=MCP_RETRY_CONFIG,
            operation_name="create_invoice"
        )
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG

    op_name = operation_name or func.__name__

    # Create retry-wrapped version of the function
    @retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(
            multiplier=config.multiplier,
            min=config.min_wait,
            max=config.max_wait
        ),
        retry=retry_if_exception_type(config.retry_exceptions),
        before_sleep=before_sleep_log(logger, structlog.INFO)
    )
    async def retry_wrapper():
        return await func(*args, **kwargs)

    # Wrap with circuit breaker
    try:
        logger.info(
            "retry_with_circuit_breaker_start",
            operation=op_name,
            max_attempts=config.max_attempts
        )

        result = await circuit_breaker(retry_wrapper)()

        logger.info(
            "retry_with_circuit_breaker_success",
            operation=op_name
        )

        return result

    except RetryError as e:
        logger.error(
            "retry_with_circuit_breaker_exhausted",
            operation=op_name,
            max_attempts=config.max_attempts,
            error=str(e)
        )
        raise

    except Exception as e:
        logger.error(
            "retry_with_circuit_breaker_failed",
            operation=op_name,
            error_type=type(e).__name__,
            error=str(e)
        )
        raise


class RetryableOperation:
    """
    Context manager for retryable operations with detailed logging.

    Provides structured logging of retry attempts and outcomes.
    """

    def __init__(
        self,
        operation_name: str,
        config: Optional[RetryConfig] = None
    ):
        """
        Initialize retryable operation.

        Args:
            operation_name: Name of the operation
            config: Retry configuration
        """
        self.operation_name = operation_name
        self.config = config or DEFAULT_RETRY_CONFIG
        self.attempt = 0
        self.last_error: Optional[Exception] = None

    async def __aenter__(self):
        """Enter async context."""
        self.attempt += 1
        logger.debug(
            "retry_operation_attempt",
            operation=self.operation_name,
            attempt=self.attempt,
            max_attempts=self.config.max_attempts
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if exc_type is None:
            logger.debug(
                "retry_operation_success",
                operation=self.operation_name,
                attempt=self.attempt
            )
            return True

        self.last_error = exc_val

        if self.attempt < self.config.max_attempts:
            # Calculate wait time
            wait_time = min(
                self.config.min_wait * (self.config.multiplier ** (self.attempt - 1)),
                self.config.max_wait
            )

            logger.warning(
                "retry_operation_failed_will_retry",
                operation=self.operation_name,
                attempt=self.attempt,
                max_attempts=self.config.max_attempts,
                error_type=exc_type.__name__,
                error=str(exc_val),
                wait_time=wait_time
            )

            # Suppress exception to allow retry
            return True
        else:
            logger.error(
                "retry_operation_exhausted",
                operation=self.operation_name,
                attempt=self.attempt,
                max_attempts=self.config.max_attempts,
                error_type=exc_type.__name__,
                error=str(exc_val)
            )

            # Let exception propagate
            return False


def should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exception: Exception to evaluate

    Returns:
        True if should retry, False otherwise
    """
    # Don't retry on these exception types
    non_retryable = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
    )

    if isinstance(exception, non_retryable):
        return False

    # Retry on network/connection errors
    retryable_names = (
        "ConnectionError",
        "TimeoutError",
        "HTTPError",
        "RequestException",
        "NetworkError",
    )

    exception_name = type(exception).__name__
    return any(name in exception_name for name in retryable_names)
