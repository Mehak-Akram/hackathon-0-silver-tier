"""
Risk classification engine for Gold Tier Autonomous AI Employee.

Implements hybrid rule-based weighted scoring system with override rules
for deterministic, auditable, and configurable risk assessment.
"""
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml


class RiskLevel(str, Enum):
    """Risk classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OperationType(str, Enum):
    """Types of operations."""
    READ = "read"
    WRITE = "write"
    IRREVERSIBLE = "irreversible"


class DataSensitivity(str, Enum):
    """Data sensitivity levels."""
    PUBLIC = "public"
    BUSINESS = "business"
    FINANCIAL = "financial"
    PII = "pii"


class Reversibility(str, Enum):
    """Reversibility levels."""
    FULLY_REVERSIBLE = "fully_reversible"
    ROLLBACK_AVAILABLE = "rollback_available"
    CANNOT_UNDO = "cannot_undo"


@dataclass
class ActionContext:
    """Context for risk classification."""
    action_type: str
    operation_type: OperationType
    data_sensitivity: DataSensitivity
    reversibility: Reversibility
    financial_impact: float  # Dollar amount
    external_visibility: str  # "internal", "business", "public"
    approval_history: str  # "pre_approved", "similar_approved", "never_approved"
    system_count: int = 1  # Number of external systems involved
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "action_type": self.action_type,
            "operation_type": self.operation_type.value,
            "data_sensitivity": self.data_sensitivity.value,
            "reversibility": self.reversibility.value,
            "financial_impact": self.financial_impact,
            "external_visibility": self.external_visibility,
            "approval_history": self.approval_history,
            "system_count": self.system_count,
            "description": self.description
        }


@dataclass
class RiskScore:
    """Risk assessment result."""
    risk_level: RiskLevel
    total_score: int
    base_score: int
    context_modifiers: int
    override_triggered: bool
    override_reason: Optional[str]
    factor_scores: Dict[str, int]
    reasoning: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "risk_level": self.risk_level.value,
            "total_score": self.total_score,
            "base_score": self.base_score,
            "context_modifiers": self.context_modifiers,
            "override_triggered": self.override_triggered,
            "override_reason": self.override_reason,
            "factor_scores": self.factor_scores,
            "reasoning": self.reasoning
        }


class RiskClassificationEngine:
    """
    Hybrid rule-based risk classification engine.

    Uses weighted scoring across 6 factors with override rules
    for deterministic, auditable risk assessment.
    """

    # Default configuration
    DEFAULT_CONFIG = {
        "thresholds": {
            "low_max": 30,
            "medium_max": 60
        },
        "weights": {
            "operation": 30,
            "sensitivity": 25,
            "reversibility": 20,
            "financial": 15,
            "visibility": 5,
            "history": 5
        },
        "operation_scores": {
            "read": 0,
            "write": 50,
            "irreversible": 100
        },
        "sensitivity_scores": {
            "public": 0,
            "business": 40,
            "financial": 80,
            "pii": 100
        },
        "reversibility_scores": {
            "fully_reversible": 0,
            "rollback_available": 50,
            "cannot_undo": 100
        },
        "financial_thresholds": [
            {"max": 0, "score": 0},
            {"max": 1000, "score": 50},
            {"max": float('inf'), "score": 100}
        ],
        "visibility_scores": {
            "internal": 0,
            "business": 50,
            "public": 100
        },
        "history_scores": {
            "pre_approved": 0,
            "similar_approved": 50,
            "never_approved": 100
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize risk engine.

        Args:
            config_path: Optional path to YAML configuration file
        """
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self.DEFAULT_CONFIG.copy()

    def classify_action(self, context: ActionContext) -> RiskScore:
        """
        Classify action risk level.

        Args:
            context: Action context with all classification factors

        Returns:
            RiskScore with level, scores, and reasoning
        """
        reasoning = []

        # Tier 1: Check override rules
        override_result = self._check_overrides(context)
        if override_result:
            override_reason, override_reasoning = override_result
            reasoning.extend(override_reasoning)
            return RiskScore(
                risk_level=RiskLevel.HIGH,
                total_score=100,
                base_score=100,
                context_modifiers=0,
                override_triggered=True,
                override_reason=override_reason,
                factor_scores={},
                reasoning=reasoning
            )

        # Tier 2: Calculate weighted scores
        factor_scores = self._calculate_factor_scores(context)
        base_score = self._calculate_base_score(factor_scores)
        reasoning.append(f"Base score: {base_score} (from weighted factors)")

        # Tier 3: Apply context modifiers
        context_modifiers = self._context_modifiers(context)
        total_score = min(100, max(0, base_score + context_modifiers))

        if context_modifiers != 0:
            reasoning.append(f"Context modifiers: {context_modifiers:+d}")
        reasoning.append(f"Total score: {total_score}")

        # Determine risk level
        risk_level = self._classify_score(total_score)
        reasoning.append(f"Risk level: {risk_level.value}")

        return RiskScore(
            risk_level=risk_level,
            total_score=total_score,
            base_score=base_score,
            context_modifiers=context_modifiers,
            override_triggered=False,
            override_reason=None,
            factor_scores=factor_scores,
            reasoning=reasoning
        )

    def _check_overrides(self, context: ActionContext) -> Optional[tuple[str, List[str]]]:
        """
        Check override rules for automatic HIGH risk.

        Returns:
            Tuple of (reason, reasoning_list) if override triggered, None otherwise
        """
        reasoning = []

        # Override 1: Accounting data modification
        if (context.data_sensitivity == DataSensitivity.FINANCIAL and
            context.operation_type in [OperationType.WRITE, OperationType.IRREVERSIBLE]):
            reasoning.append("Override: Financial data modification")
            return ("Financial data modification", reasoning)

        # Override 2: Large financial transaction
        if context.financial_impact > 1000:
            reasoning.append(f"Override: Financial impact ${context.financial_impact} > $1000")
            return (f"Financial transaction exceeds $1000 (${context.financial_impact})", reasoning)

        # Override 3: Irreversible operation without rollback
        if (context.operation_type == OperationType.IRREVERSIBLE and
            context.reversibility == Reversibility.CANNOT_UNDO):
            reasoning.append("Override: Irreversible operation with no rollback")
            return ("Irreversible operation without rollback procedure", reasoning)

        # Override 4: Multi-system operations
        if context.system_count > 2:
            reasoning.append(f"Override: Multi-system operation ({context.system_count} systems)")
            return (f"Multi-system operation ({context.system_count} systems)", reasoning)

        # Override 5: First-time action (never approved)
        if (context.approval_history == "never_approved" and
            context.operation_type != OperationType.READ):
            reasoning.append("Override: First-time action (never approved)")
            return ("First-time action requiring approval", reasoning)

        return None

    def _calculate_factor_scores(self, context: ActionContext) -> Dict[str, int]:
        """Calculate raw scores for each factor."""
        scores = {}

        # Operation type
        scores["operation"] = self.config["operation_scores"][context.operation_type.value]

        # Data sensitivity
        scores["sensitivity"] = self.config["sensitivity_scores"][context.data_sensitivity.value]

        # Reversibility
        scores["reversibility"] = self.config["reversibility_scores"][context.reversibility.value]

        # Financial impact
        for threshold in self.config["financial_thresholds"]:
            if context.financial_impact <= threshold["max"]:
                scores["financial"] = threshold["score"]
                break

        # External visibility
        scores["visibility"] = self.config["visibility_scores"].get(
            context.external_visibility, 50
        )

        # Approval history
        scores["history"] = self.config["history_scores"].get(
            context.approval_history, 100
        )

        return scores

    def _calculate_base_score(self, factor_scores: Dict[str, int]) -> int:
        """Calculate weighted base score from factor scores."""
        weights = self.config["weights"]
        total = 0

        for factor, score in factor_scores.items():
            weight = weights.get(factor, 0)
            # Normalize: score is 0-100, weight is percentage
            total += (score * weight) / 100

        return int(round(total))

    def _context_modifiers(self, context: ActionContext) -> int:
        """Apply context-based score modifiers."""
        modifiers = 0

        # Reduce risk for read-only operations
        if context.operation_type == OperationType.READ:
            modifiers -= 10

        # Increase risk for public visibility
        if context.external_visibility == "public":
            modifiers += 10

        # Reduce risk for pre-approved actions
        if context.approval_history == "pre_approved":
            modifiers -= 15

        return modifiers

    def _classify_score(self, score: int) -> RiskLevel:
        """Classify score into risk level."""
        thresholds = self.config["thresholds"]

        if score <= thresholds["low_max"]:
            return RiskLevel.LOW
        elif score <= thresholds["medium_max"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH


# Global risk engine instance
risk_engine = RiskClassificationEngine()
