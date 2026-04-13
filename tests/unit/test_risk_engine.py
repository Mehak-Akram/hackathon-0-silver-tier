"""
Unit tests for Risk Engine.

Tests the risk classification logic in isolation.
"""
import pytest
from src.risk_engine import (
    RiskClassificationEngine,
    ActionContext,
    OperationType,
    DataSensitivity,
    Reversibility,
    RiskLevel
)


@pytest.mark.unit
class TestRiskClassificationEngine:
    """Test suite for RiskClassificationEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RiskClassificationEngine()

    def test_low_risk_read_operation(self):
        """Test that read operations are classified as low risk."""
        context = ActionContext(
            action_type="fetch_data",
            operation_type=OperationType.READ,
            data_sensitivity=DataSensitivity.PUBLIC,
            reversibility=Reversibility.FULLY_REVERSIBLE,
            financial_impact=0.0,
            external_visibility="internal",
            approval_history="pre_approved"
        )

        result = self.engine.classify_action(context)

        assert result.risk_level == RiskLevel.LOW
        assert result.override_triggered is False

    def test_high_risk_financial_write(self):
        """Test that financial write operations are high risk."""
        context = ActionContext(
            action_type="create_invoice",
            operation_type=OperationType.WRITE,
            data_sensitivity=DataSensitivity.FINANCIAL,
            reversibility=Reversibility.ROLLBACK_AVAILABLE,
            financial_impact=500.0,
            external_visibility="business",
            approval_history="never_approved"
        )

        result = self.engine.classify_action(context)

        assert result.risk_level == RiskLevel.HIGH
        assert result.override_triggered is True
        assert "Financial data modification" in result.override_reason

    def test_high_risk_large_transaction(self):
        """Test that large financial transactions trigger override."""
        context = ActionContext(
            action_type="create_invoice",
            operation_type=OperationType.WRITE,
            data_sensitivity=DataSensitivity.BUSINESS,
            reversibility=Reversibility.ROLLBACK_AVAILABLE,
            financial_impact=5000.0,  # > $1000 threshold
            external_visibility="business",
            approval_history="similar_approved"
        )

        result = self.engine.classify_action(context)

        assert result.risk_level == RiskLevel.HIGH
        assert result.override_triggered is True
        assert "$5000" in result.override_reason

    def test_medium_risk_business_write(self):
        """Test that business write operations are medium risk."""
        context = ActionContext(
            action_type="send_email",
            operation_type=OperationType.WRITE,
            data_sensitivity=DataSensitivity.BUSINESS,
            reversibility=Reversibility.CANNOT_UNDO,
            financial_impact=0.0,
            external_visibility="business",
            approval_history="similar_approved"
        )

        result = self.engine.classify_action(context)

        # Should be medium or high depending on scoring
        assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_irreversible_operation_override(self):
        """Test that irreversible operations without rollback trigger override."""
        context = ActionContext(
            action_type="delete_data",
            operation_type=OperationType.IRREVERSIBLE,
            data_sensitivity=DataSensitivity.BUSINESS,
            reversibility=Reversibility.CANNOT_UNDO,
            financial_impact=0.0,
            external_visibility="internal",
            approval_history="never_approved"
        )

        result = self.engine.classify_action(context)

        assert result.risk_level == RiskLevel.HIGH
        assert result.override_triggered is True


@pytest.mark.unit
def test_risk_engine_initialization():
    """Test that risk engine initializes with default config."""
    engine = RiskClassificationEngine()
    assert engine.config is not None
    assert "thresholds" in engine.config
    assert "weights" in engine.config


@pytest.mark.unit
def test_action_context_to_dict():
    """Test ActionContext serialization."""
    context = ActionContext(
        action_type="test_action",
        operation_type=OperationType.READ,
        data_sensitivity=DataSensitivity.PUBLIC,
        reversibility=Reversibility.FULLY_REVERSIBLE,
        financial_impact=0.0,
        external_visibility="internal",
        approval_history="pre_approved",
        description="Test action"
    )

    context_dict = context.to_dict()

    assert context_dict["action_type"] == "test_action"
    assert context_dict["operation_type"] == "read"
    assert context_dict["description"] == "Test action"
