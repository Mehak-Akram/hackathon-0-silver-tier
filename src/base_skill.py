"""
Base skill class for Gold Tier Autonomous AI Employee.

Provides abstract base class for all Agent Skills with common
functionality for execution, validation, and audit logging.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone
import structlog

from src.audit_logger import audit_logger, RiskLevel, ApprovalMethod
from src.risk_engine import risk_engine, ActionContext, OperationType, DataSensitivity, Reversibility
from src.validation_engine import validation_engine


logger = structlog.get_logger("base_skill")


@dataclass
class SkillInput:
    """Input data for skill execution."""
    parameters: Dict[str, Any]
    context: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        """Get parameter value with default."""
        return self.parameters.get(key, default)

    def require(self, key: str) -> Any:
        """
        Get required parameter value.

        Raises:
            ValueError: If parameter missing
        """
        if key not in self.parameters:
            raise ValueError(f"Required parameter '{key}' missing")
        return self.parameters[key]


@dataclass
class SkillOutput:
    """Output data from skill execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    side_effects: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.side_effects is None:
            self.side_effects = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "side_effects": self.side_effects
        }


class BaseSkill(ABC):
    """
    Abstract base class for all Agent Skills.

    Provides common functionality:
    - Risk classification
    - Audit logging
    - Input validation
    - Error handling
    - Execution tracking
    """

    def __init__(self, skill_name: str):
        """
        Initialize base skill.

        Args:
            skill_name: Unique name for this skill
        """
        self.skill_name = skill_name
        self.logger = structlog.get_logger(f"skill.{skill_name}")

    @abstractmethod
    async def execute_impl(self, skill_input: SkillInput) -> SkillOutput:
        """
        Execute skill implementation.

        Subclasses must implement this method with their specific logic.

        Args:
            skill_input: Input data for execution

        Returns:
            SkillOutput with results

        Raises:
            Exception: Any execution errors
        """
        pass

    @abstractmethod
    def get_action_context(self, skill_input: SkillInput) -> ActionContext:
        """
        Get action context for risk classification.

        Subclasses must implement this to provide risk classification context.

        Args:
            skill_input: Input data

        Returns:
            ActionContext for risk engine
        """
        pass

    def validate_input(self, skill_input: SkillInput) -> bool:
        """
        Validate skill input.

        Subclasses can override to add custom validation.

        Args:
            skill_input: Input to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Default: no validation
        return True

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        approval_method: Optional[ApprovalMethod] = None
    ) -> SkillOutput:
        """
        Execute skill with full audit logging and risk classification.

        This is the main entry point for skill execution.

        Args:
            parameters: Skill parameters
            context: Execution context
            approval_method: Override approval method (for testing)

        Returns:
            SkillOutput with results
        """
        skill_input = SkillInput(
            parameters=parameters,
            context=context or {}
        )

        # Validate input
        try:
            self.validate_input(skill_input)
        except ValueError as e:
            self.logger.error(
                "skill_input_validation_failed",
                skill=self.skill_name,
                error=str(e)
            )
            return SkillOutput(
                success=False,
                result=None,
                error=f"Input validation failed: {str(e)}"
            )

        # Get action context for risk classification
        action_context = self.get_action_context(skill_input)

        # Classify risk
        risk_score = risk_engine.classify_action(action_context)

        self.logger.info(
            "skill_risk_classified",
            skill=self.skill_name,
            risk_level=risk_score.risk_level.value,
            total_score=risk_score.total_score
        )

        # Determine approval method if not provided
        if approval_method is None:
            if risk_score.risk_level == RiskLevel.LOW:
                approval_method = ApprovalMethod.AUTO_APPROVED
            elif risk_score.risk_level == RiskLevel.MEDIUM:
                # Medium risk: auto-approve for now (can be configured)
                approval_method = ApprovalMethod.AUTO_APPROVED
            else:
                # High risk: requires human approval
                approval_method = ApprovalMethod.PENDING
                self.logger.warning(
                    "skill_requires_approval",
                    skill=self.skill_name,
                    risk_level=risk_score.risk_level.value,
                    reason=risk_score.override_reason
                )
                return SkillOutput(
                    success=False,
                    result=None,
                    error=f"High-risk action requires human approval: {risk_score.override_reason}"
                )

        # Execute with audit logging
        with audit_logger.log_action(
            action_type=f"skill.{self.skill_name}",
            description=action_context.description,
            risk_level=risk_score.risk_level,
            approval_method=approval_method,
            input_data={
                "parameters": parameters,
                "context": context
            },
            skill_name=self.skill_name,
            risk_score=risk_score.total_score
        ) as log:
            try:
                # Execute implementation
                output = await self.execute_impl(skill_input)

                # Log output
                log.set_output(output.to_dict())

                # Log side effects
                for side_effect in output.side_effects:
                    log.add_side_effect(
                        effect=side_effect.get("effect", "unknown"),
                        details=side_effect.get("details", {})
                    )

                self.logger.info(
                    "skill_executed_successfully",
                    skill=self.skill_name,
                    success=output.success
                )

                return output

            except Exception as e:
                # Log error details
                log.set_error_details({
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

                self.logger.error(
                    "skill_execution_failed",
                    skill=self.skill_name,
                    error_type=type(e).__name__,
                    error=str(e),
                    exc_info=True
                )

                return SkillOutput(
                    success=False,
                    result=None,
                    error=f"{type(e).__name__}: {str(e)}"
                )

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get skill metadata.

        Subclasses can override to provide additional metadata.

        Returns:
            Dictionary with skill metadata
        """
        return {
            "skill_name": self.skill_name,
            "skill_type": self.__class__.__name__
        }


class ReadOnlySkill(BaseSkill):
    """
    Base class for read-only skills.

    Automatically sets operation type to READ for risk classification.
    """

    def get_action_context(self, skill_input: SkillInput) -> ActionContext:
        """Get action context with READ operation type."""
        return ActionContext(
            action_type=f"skill.{self.skill_name}",
            operation_type=OperationType.READ,
            data_sensitivity=self._get_data_sensitivity(skill_input),
            reversibility=Reversibility.FULLY_REVERSIBLE,
            financial_impact=0.0,
            external_visibility="internal",
            approval_history="pre_approved",
            description=self._get_description(skill_input)
        )

    @abstractmethod
    def _get_data_sensitivity(self, skill_input: SkillInput) -> DataSensitivity:
        """Get data sensitivity for this skill."""
        pass

    @abstractmethod
    def _get_description(self, skill_input: SkillInput) -> str:
        """Get human-readable description of the action."""
        pass


class WriteSkill(BaseSkill):
    """
    Base class for write skills.

    Automatically sets operation type to WRITE for risk classification.
    """

    def get_action_context(self, skill_input: SkillInput) -> ActionContext:
        """Get action context with WRITE operation type."""
        return ActionContext(
            action_type=f"skill.{self.skill_name}",
            operation_type=OperationType.WRITE,
            data_sensitivity=self._get_data_sensitivity(skill_input),
            reversibility=self._get_reversibility(skill_input),
            financial_impact=self._get_financial_impact(skill_input),
            external_visibility=self._get_external_visibility(skill_input),
            approval_history=self._get_approval_history(skill_input),
            description=self._get_description(skill_input)
        )

    @abstractmethod
    def _get_data_sensitivity(self, skill_input: SkillInput) -> DataSensitivity:
        """Get data sensitivity for this skill."""
        pass

    @abstractmethod
    def _get_reversibility(self, skill_input: SkillInput) -> Reversibility:
        """Get reversibility for this skill."""
        pass

    def _get_financial_impact(self, skill_input: SkillInput) -> float:
        """Get financial impact (default: 0.0)."""
        return 0.0

    def _get_external_visibility(self, skill_input: SkillInput) -> str:
        """Get external visibility (default: internal)."""
        return "internal"

    def _get_approval_history(self, skill_input: SkillInput) -> str:
        """Get approval history (default: similar_approved)."""
        return "similar_approved"

    @abstractmethod
    def _get_description(self, skill_input: SkillInput) -> str:
        """Get human-readable description of the action."""
        pass
