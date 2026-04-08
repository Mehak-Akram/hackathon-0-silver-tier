"""
MCP Tool Call Auditing Wrapper.

Wraps MCP tool calls with comprehensive audit logging.
"""
import json
from datetime import datetime
from typing import Dict, Any, Callable
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger import audit_logger, RiskLevel, ApprovalMethod
from shared.logging_config import get_logger

logger = get_logger(__name__, "mcp-audit.log")


class MCPAuditWrapper:
    """
    Audit wrapper for MCP tool calls.

    Logs all MCP tool invocations with complete context.
    """

    # Risk classification for different tool types
    TOOL_RISK_LEVELS = {
        "send_email": RiskLevel.MEDIUM,
        "post_facebook_page": RiskLevel.MEDIUM,
        "post_twitter": RiskLevel.MEDIUM,
        "post_instagram": RiskLevel.MEDIUM,
        "create_customer": RiskLevel.LOW,
        "create_invoice": RiskLevel.HIGH,
        "fetch_financial_summary": RiskLevel.LOW,
        "generate_ceo_briefing": RiskLevel.LOW
    }

    @staticmethod
    def wrap_tool_call(tool_name: str, handler: Callable) -> Callable:
        """
        Wrap a tool handler with audit logging.

        Args:
            tool_name: Name of the MCP tool
            handler: Original handler function

        Returns:
            Wrapped handler with audit logging
        """
        async def wrapped_handler(arguments: dict):
            """Wrapped handler with audit logging."""

            # Determine risk level
            risk_level = MCPAuditWrapper.TOOL_RISK_LEVELS.get(
                tool_name,
                RiskLevel.MEDIUM
            )

            # Log the tool call
            with audit_logger.log_action(
                action_type=f"mcp.{tool_name}",
                description=f"MCP tool call: {tool_name}",
                risk_level=risk_level,
                approval_method=ApprovalMethod.AUTO_APPROVED,
                input_data=arguments,
                tool_name=tool_name
            ) as log:
                # Execute the handler
                result = await handler(arguments)

                # Parse result
                if result and len(result) > 0:
                    result_text = result[0].text
                    try:
                        result_data = json.loads(result_text)
                        log.set_output(result_data)

                        # Track side effects
                        if result_data.get("success"):
                            if tool_name == "send_email":
                                log.add_side_effect("email_sent", {
                                    "recipient": arguments.get("to")
                                })
                            elif tool_name in ["post_facebook_page", "post_twitter", "post_instagram"]:
                                log.add_side_effect("social_media_post", {
                                    "platform": tool_name.replace("post_", ""),
                                    "post_id": result_data.get("post_id")
                                })
                            elif tool_name == "create_customer":
                                log.add_side_effect("customer_created", {
                                    "customer_id": result_data.get("customer_id")
                                })
                            elif tool_name == "create_invoice":
                                log.add_side_effect("invoice_created", {
                                    "invoice_id": result_data.get("invoice_id"),
                                    "amount": result_data.get("amount")
                                })
                        else:
                            log.set_error_details({
                                "error_code": result_data.get("error"),
                                "error_message": result_data.get("message")
                            })

                    except json.JSONDecodeError:
                        log.set_output({"raw_result": result_text})

                return result

        return wrapped_handler

    @staticmethod
    def log_mcp_call(tool_name: str, arguments: dict, result: Dict[str, Any]):
        """
        Log an MCP tool call (alternative to wrapper for sync logging).

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            result: Tool result
        """
        risk_level = MCPAuditWrapper.TOOL_RISK_LEVELS.get(
            tool_name,
            RiskLevel.MEDIUM
        )

        logger.info(
            "mcp_tool_call",
            tool_name=tool_name,
            risk_level=risk_level.value,
            arguments=arguments,
            result=result,
            success=result.get("success", False),
            timestamp=datetime.now().isoformat()
        )


if __name__ == "__main__":
    # Test audit wrapper
    print("MCP Audit Wrapper initialized")
    print(f"Tool risk levels: {MCPAuditWrapper.TOOL_RISK_LEVELS}")
