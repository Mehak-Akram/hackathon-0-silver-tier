"""
CEO Briefing model for Gold Tier Autonomous AI Employee.

Represents a weekly executive summary report.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum


class BriefingStatus(str, Enum):
    """CEO briefing generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    DELIVERED = "delivered"


class DataSourceStatus(str, Enum):
    """Status of data source for briefing."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"


class CEOBriefing(BaseModel):
    """
    CEO Briefing entity representing a weekly executive summary.

    Attributes:
        briefing_id: Unique briefing identifier
        generation_date: Date briefing was generated
        week_start: Start date of reporting period
        week_end: End date of reporting period
        status: Briefing generation status
        file_path: Path to generated briefing file

        financial_summary: Financial performance data
        marketing_metrics: Marketing performance data
        operational_highlights: Business operations summary
        risk_alerts: Risk and issue alerts

        data_sources: Status of each data source
        missing_data: List of missing data sections

        delivered_at: Timestamp when briefing was delivered
        delivered_to: List of recipients
        delivery_method: How briefing was delivered (email, file, etc.)

        metadata: Additional briefing metadata
    """

    briefing_id: str = Field(..., description="Unique briefing identifier")
    generation_date: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    week_start: date = Field(..., description="Reporting period start")
    week_end: date = Field(..., description="Reporting period end")
    status: BriefingStatus = Field(default=BriefingStatus.PENDING, description="Briefing status")
    file_path: Optional[str] = Field(default=None, description="Generated file path")

    # Content sections
    financial_summary: Dict[str, Any] = Field(default_factory=dict, description="Financial data")
    marketing_metrics: Dict[str, Any] = Field(default_factory=dict, description="Marketing data")
    operational_highlights: Dict[str, Any] = Field(default_factory=dict, description="Operations data")
    risk_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Risk alerts")

    # Data source tracking
    data_sources: Dict[str, DataSourceStatus] = Field(
        default_factory=lambda: {
            "twitter": DataSourceStatus.AVAILABLE,
            "instagram": DataSourceStatus.AVAILABLE,
            "facebook": DataSourceStatus.AVAILABLE,
            "tasks": DataSourceStatus.AVAILABLE
        },
        description="Data source status"
    )
    missing_data: List[str] = Field(default_factory=list, description="Missing data sections")

    # Delivery tracking
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery timestamp")
    delivered_to: List[str] = Field(default_factory=list, description="Recipients")
    delivery_method: Optional[str] = Field(default=None, description="Delivery method")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def mark_generating(self) -> None:
        """Mark briefing as generating."""
        self.status = BriefingStatus.GENERATING

    def mark_completed(self, file_path: str) -> None:
        """
        Mark briefing as completed.

        Args:
            file_path: Path to generated briefing file
        """
        self.status = BriefingStatus.COMPLETED
        self.file_path = file_path

    def mark_failed(self, error: str) -> None:
        """
        Mark briefing as failed.

        Args:
            error: Error message
        """
        self.status = BriefingStatus.FAILED
        self.metadata["error"] = error

    def mark_delivered(self, recipients: List[str], method: str) -> None:
        """
        Mark briefing as delivered.

        Args:
            recipients: List of recipient emails
            method: Delivery method (e.g., "email", "file")
        """
        self.status = BriefingStatus.DELIVERED
        self.delivered_at = datetime.now()
        self.delivered_to = recipients
        self.delivery_method = method

    def set_data_source_status(self, source: str, status: DataSourceStatus) -> None:
        """
        Set status for a data source.

        Args:
            source: Data source name (e.g., "social", "twitter")
            status: Source status
        """
        self.data_sources[source] = status
        if status == DataSourceStatus.UNAVAILABLE:
            self.missing_data.append(source)

    def add_financial_data(self, data: Dict[str, Any]) -> None:
        """
        Add financial summary data.

        Args:
            data: Financial data dictionary
        """
        self.financial_summary = data

    def add_marketing_data(self, data: Dict[str, Any]) -> None:
        """
        Add marketing metrics data.

        Args:
            data: Marketing data dictionary
        """
        self.marketing_metrics = data

    def add_operational_data(self, data: Dict[str, Any]) -> None:
        """
        Add operational highlights data.

        Args:
            data: Operations data dictionary
        """
        self.operational_highlights = data

    def add_risk_alert(self, severity: str, category: str, message: str) -> None:
        """
        Add risk alert to briefing.

        Args:
            severity: Alert severity (low/medium/high)
            category: Alert category (financial/operational/security)
            message: Alert message
        """
        self.risk_alerts.append({
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def is_complete(self) -> bool:
        """Check if briefing has all required data."""
        return (
            bool(self.financial_summary) and
            bool(self.marketing_metrics) and
            bool(self.operational_highlights)
        )

    def has_missing_data(self) -> bool:
        """Check if briefing has missing data sections."""
        return len(self.missing_data) > 0

    def get_completeness_percentage(self) -> float:
        """
        Calculate briefing completeness percentage.

        Returns:
            Completeness percentage (0-100)
        """
        total_sources = len(self.data_sources)
        available_sources = sum(
            1 for status in self.data_sources.values()
            if status == DataSourceStatus.AVAILABLE
        )
        return (available_sources / total_sources) * 100 if total_sources > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert briefing to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert briefing to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CEOBriefing":
        """
        Create briefing from dictionary.

        Args:
            data: Briefing data dictionary

        Returns:
            CEOBriefing instance
        """
        return cls(**data)
