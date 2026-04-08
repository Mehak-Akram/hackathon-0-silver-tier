"""
Circuit breaker pattern implementation for Gold Tier Autonomous AI Employee.

Provides fail-fast mechanism for MCP server failures using aiobreaker library
with per-server configuration and state monitoring.
"""
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import structlog
from aiobreaker import CircuitBreaker, CircuitBreakerError, CircuitBreakerState


logger = structlog.get_logger("circuit_breaker")


class ServerType(str, Enum):
    """MCP server types."""
    SOCIAL = "social"
    EMAIL = "email"
    REPORTING = "reporting"


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker."""
    fail_max: int  # Number of failures before opening
    timeout_duration: int  # Seconds before attempting half-open
    name: str


class CircuitBreakerManager:
    """
    Manages circuit breakers for multiple MCP servers.

    Provides per-server circuit breakers with state monitoring
    and automatic recovery testing.
    """

    # Default configurations per server type
    DEFAULT_CONFIGS = {
        ServerType.SOCIAL: CircuitBreakerConfig(
            fail_max=3,
            timeout_duration=180,  # 3 minutes
            name="social-mcp"
        ),
        ServerType.EMAIL: CircuitBreakerConfig(
            fail_max=3,
            timeout_duration=180,  # 3 minutes
            name="email-mcp"
        ),
        ServerType.REPORTING: CircuitBreakerConfig(
            fail_max=5,
            timeout_duration=300,  # 5 minutes
            name="reporting-mcp"
        ),
    }

    def __init__(self, custom_configs: Optional[Dict[ServerType, CircuitBreakerConfig]] = None):
        """
        Initialize circuit breaker manager.

        Args:
            custom_configs: Optional custom configurations per server type
        """
        self.configs = self.DEFAULT_CONFIGS.copy()
        if custom_configs:
            self.configs.update(custom_configs)

        self.breakers: Dict[ServerType, CircuitBreaker] = {}
        self._initialize_breakers()

    def _initialize_breakers(self):
        """Initialize circuit breakers for all server types."""
        for server_type, config in self.configs.items():
            breaker = CircuitBreaker(
                fail_max=config.fail_max,
                timeout_duration=config.timeout_duration,
                name=config.name
            )

            # Register state change listener
            breaker.add_listener(self._create_state_listener(server_type))

            self.breakers[server_type] = breaker

            logger.info(
                "circuit_breaker_initialized",
                server_type=server_type.value,
                fail_max=config.fail_max,
                timeout_duration=config.timeout_duration
            )

    def _create_state_listener(self, server_type: ServerType) -> Callable:
        """
        Create state change listener for a server.

        Args:
            server_type: Server type for this listener

        Returns:
            Listener function
        """
        def on_state_change(breaker: CircuitBreaker, old_state: CircuitBreakerState,
                           new_state: CircuitBreakerState):
            """Handle circuit breaker state changes."""
            logger.warning(
                "circuit_breaker_state_change",
                server_type=server_type.value,
                breaker_name=breaker.name,
                old_state=old_state.name,
                new_state=new_state.name,
                fail_counter=breaker.fail_counter,
                failure_count=breaker.failure_count
            )

            # Emit specific alerts based on state
            if new_state == CircuitBreakerState.STATE_OPEN:
                logger.critical(
                    "circuit_breaker_opened",
                    server_type=server_type.value,
                    breaker_name=breaker.name,
                    message=f"Circuit breaker opened for {server_type.value} - service unavailable",
                    failure_count=breaker.failure_count
                )
            elif new_state == CircuitBreakerState.STATE_HALF_OPEN:
                logger.warning(
                    "circuit_breaker_half_open",
                    server_type=server_type.value,
                    breaker_name=breaker.name,
                    message=f"Circuit breaker testing recovery for {server_type.value}"
                )
            elif new_state == CircuitBreakerState.STATE_CLOSED:
                logger.info(
                    "circuit_breaker_closed",
                    server_type=server_type.value,
                    breaker_name=breaker.name,
                    message=f"Circuit breaker closed for {server_type.value} - service recovered"
                )

        return on_state_change

    def get_breaker(self, server_type: ServerType) -> CircuitBreaker:
        """
        Get circuit breaker for a server type.

        Args:
            server_type: Server type

        Returns:
            CircuitBreaker instance

        Raises:
            KeyError: If server type not configured
        """
        if server_type not in self.breakers:
            raise KeyError(f"No circuit breaker configured for {server_type.value}")
        return self.breakers[server_type]

    async def call_with_breaker(
        self,
        server_type: ServerType,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call a function with circuit breaker protection.

        Args:
            server_type: Server type for circuit breaker selection
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from func
        """
        breaker = self.get_breaker(server_type)

        try:
            # Use circuit breaker as decorator
            protected_func = breaker(func)
            result = await protected_func(*args, **kwargs)

            logger.debug(
                "circuit_breaker_call_success",
                server_type=server_type.value,
                state=breaker.current_state.name,
                fail_counter=breaker.fail_counter
            )

            return result

        except CircuitBreakerError as e:
            logger.error(
                "circuit_breaker_call_rejected",
                server_type=server_type.value,
                state=breaker.current_state.name,
                error=str(e)
            )
            raise

        except Exception as e:
            logger.error(
                "circuit_breaker_call_failed",
                server_type=server_type.value,
                state=breaker.current_state.name,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise

    def get_state(self, server_type: ServerType) -> str:
        """
        Get current state of circuit breaker.

        Args:
            server_type: Server type

        Returns:
            State name (CLOSED, OPEN, HALF_OPEN)
        """
        breaker = self.get_breaker(server_type)
        return breaker.current_state.name

    def get_failure_count(self, server_type: ServerType) -> int:
        """
        Get failure count for circuit breaker.

        Args:
            server_type: Server type

        Returns:
            Number of failures
        """
        breaker = self.get_breaker(server_type)
        return breaker.failure_count

    def reset(self, server_type: ServerType):
        """
        Manually reset circuit breaker to closed state.

        Args:
            server_type: Server type
        """
        breaker = self.get_breaker(server_type)
        breaker.close()

        logger.info(
            "circuit_breaker_reset",
            server_type=server_type.value,
            message=f"Circuit breaker manually reset for {server_type.value}"
        )

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get states of all circuit breakers.

        Returns:
            Dictionary mapping server type to state info
        """
        states = {}
        for server_type, breaker in self.breakers.items():
            states[server_type.value] = {
                "state": breaker.current_state.name,
                "failure_count": breaker.failure_count,
                "fail_counter": breaker.fail_counter,
                "fail_max": breaker.fail_max,
                "timeout_duration": breaker.timeout_duration
            }
        return states


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()
