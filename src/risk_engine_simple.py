"""
Simplified Risk Engine - No External Dependencies.

Provides basic risk assessment without complex dependencies.
"""
from typing import Dict, Any, Tuple


class RiskEngine:
    """Simplified risk assessment engine."""

    def __init__(self):
        """Initialize risk engine with basic rules."""
        self.high_risk_actions = {
            "delete_file", "delete_data", "drop_table", "send_money",
            "create_invoice", "approve_payment", "modify_permissions"
        }

        self.medium_risk_actions = {
            "send_email", "create_customer", "update_data",
            "generate_report", "modify_config"
        }

    def assess_risk(self, action: str, context: Dict[str, Any]) -> Tuple[str, float]:
        """
        Assess risk level for an action.

        Args:
            action: Action type (e.g., "create_invoice")
            context: Context dictionary with details

        Returns:
            Tuple of (risk_level, risk_score)
        """
        # Check for high-risk actions
        if action in self.high_risk_actions:
            return ("high", 0.8)

        # Check for medium-risk actions
        if action in self.medium_risk_actions:
            return ("medium", 0.5)

        # Check context for risk factors
        if context.get("amount", 0) > 1000:
            return ("high", 0.75)

        if context.get("external", False):
            return ("medium", 0.6)

        # Default to low risk
        return ("low", 0.2)
