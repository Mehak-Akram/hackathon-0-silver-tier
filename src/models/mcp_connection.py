"""
MCP Connection model for Gold Tier Autonomous AI Employee.

Represents a connection to an MCP server.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MCPServerType(str, Enum):
    """MCP server types."""
    SOCIAL = "social"
    EMAIL = "email"
    REPORTING = "reporting"
    CUSTOM = "custom"


class ConnectionStatus(str, Enum):
    """MCP connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    DEGRADED = "degraded"


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MCPConnection(BaseModel):
    """
    MCP Connection entity representing a connection to an MCP server.

    Attributes:
        connection_id: Unique connection identifier
        server_type: Type of MCP server
        server_name: Human-readable server name
        server_url: Server URL or endpoint
        status: Current connection status
        health_status: Health check status

        connected_at: Timestamp when connection was established
        last_health_check: Timestamp of last health check
        last_request: Timestamp of last request
        last_error: Timestamp of last error

        error_count: Total error count
        consecutive_errors: Consecutive error count
        success_count: Total success count
        request_count: Total request count

        circuit_breaker_open: Whether circuit breaker is open
        circuit_breaker_opened_at: When circuit breaker was opened

        metadata: Additional connection metadata
        config: Connection configuration
    """

    connection_id: str = Field(..., description="Unique connection identifier")
    server_type: MCPServerType = Field(..., description="Server type")
    server_name: str = Field(..., description="Server name")
    server_url: Optional[str] = Field(default=None, description="Server URL")
    status: ConnectionStatus = Field(default=ConnectionStatus.DISCONNECTED, description="Connection status")
    health_status: HealthStatus = Field(default=HealthStatus.UNKNOWN, description="Health status")

    # Timestamps
    connected_at: Optional[datetime] = Field(default=None, description="Connection timestamp")
    last_health_check: Optional[datetime] = Field(default=None, description="Last health check")
    last_request: Optional[datetime] = Field(default=None, description="Last request timestamp")
    last_error: Optional[datetime] = Field(default=None, description="Last error timestamp")

    # Metrics
    error_count: int = Field(default=0, description="Total errors")
    consecutive_errors: int = Field(default=0, description="Consecutive errors")
    success_count: int = Field(default=0, description="Total successes")
    request_count: int = Field(default=0, description="Total requests")

    # Circuit breaker
    circuit_breaker_open: bool = Field(default=False, description="Circuit breaker status")
    circuit_breaker_opened_at: Optional[datetime] = Field(default=None, description="Circuit breaker open time")

    # Configuration
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    config: Dict[str, Any] = Field(default_factory=dict, description="Connection config")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def mark_connected(self) -> None:
        """Mark connection as connected."""
        self.status = ConnectionStatus.CONNECTED
        self.connected_at = datetime.now()
        self.health_status = HealthStatus.HEALTHY

    def mark_disconnected(self) -> None:
        """Mark connection as disconnected."""
        self.status = ConnectionStatus.DISCONNECTED
        self.health_status = HealthStatus.UNKNOWN

    def mark_error(self, error: str) -> None:
        """
        Mark connection error.

        Args:
            error: Error message
        """
        self.status = ConnectionStatus.ERROR
        self.health_status = HealthStatus.UNHEALTHY
        self.last_error = datetime.now()
        self.error_count += 1
        self.consecutive_errors += 1
        self.metadata["last_error_message"] = error

    def mark_success(self) -> None:
        """Mark successful request."""
        self.status = ConnectionStatus.CONNECTED
        self.health_status = HealthStatus.HEALTHY
        self.last_request = datetime.now()
        self.success_count += 1
        self.consecutive_errors = 0  # Reset consecutive errors

    def record_request(self) -> None:
        """Record a request."""
        self.request_count += 1
        self.last_request = datetime.now()

    def update_health_check(self, is_healthy: bool) -> None:
        """
        Update health check status.

        Args:
            is_healthy: Whether server is healthy
        """
        self.last_health_check = datetime.now()
        self.health_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY

        if not is_healthy:
            self.status = ConnectionStatus.DEGRADED

    def open_circuit_breaker(self) -> None:
        """Open circuit breaker."""
        self.circuit_breaker_open = True
        self.circuit_breaker_opened_at = datetime.now()
        self.status = ConnectionStatus.ERROR

    def close_circuit_breaker(self) -> None:
        """Close circuit breaker."""
        self.circuit_breaker_open = False
        self.circuit_breaker_opened_at = None
        self.status = ConnectionStatus.CONNECTED
        self.consecutive_errors = 0

    def should_open_circuit_breaker(self, threshold: int = 5) -> bool:
        """
        Check if circuit breaker should open.

        Args:
            threshold: Consecutive error threshold

        Returns:
            True if circuit breaker should open
        """
        return self.consecutive_errors >= threshold

    def get_error_rate(self) -> float:
        """
        Calculate error rate.

        Returns:
            Error rate (0-1)
        """
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

    def get_success_rate(self) -> float:
        """
        Calculate success rate.

        Returns:
            Success rate (0-1)
        """
        if self.request_count == 0:
            return 0.0
        return self.success_count / self.request_count

    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return (
            self.status == ConnectionStatus.CONNECTED and
            self.health_status == HealthStatus.HEALTHY and
            not self.circuit_breaker_open
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert connection to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPConnection":
        """
        Create connection from dictionary.

        Args:
            data: Connection data dictionary

        Returns:
            MCPConnection instance
        """
        return cls(**data)
