"""
MCP Server for Gold Tier AI Employee.

Provides external integration functions with rate limiting and logging:
- Email (send_email)
- Social Media (post_facebook_page, post_twitter, post_instagram)
- Reporting (generate_ceo_briefing)
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Warning: MCP SDK not available. Install with: pip install mcp")
    Server = None

# Import local modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from mcp_server.rate_limiter import RateLimiter
from src.odoo_client import OdooClient

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__, "mcp-server.log")

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> Dict[str, Any]:
    """Load MCP server configuration from config.json."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Substitute environment variables
    config_str = json.dumps(config)
    for key, value in os.environ.items():
        config_str = config_str.replace(f"${{{key}}}", value)

    return json.loads(config_str)


class GoldTierMCPServer:
    """
    MCP Server for Gold Tier external integrations.

    Provides comprehensive business automation tools:
    - Email and social media posting
    - Financial reporting and CEO briefings
    """

    def __init__(self):
        """Initialize MCP server with configuration."""
        self.config = load_config()
        self.server_name = self.config["server_name"]
        self.version = self.config["version"]

        # Initialize rate limiter
        rate_limits = {
            "send_email": self.config["rate_limits"]["email_per_hour"],
            "post_facebook_page": self.config["rate_limits"]["facebook_per_hour"],
            "post_twitter": self.config["rate_limits"]["twitter_per_hour"],
            "post_instagram": self.config["rate_limits"]["instagram_per_hour"],
            "generate_ceo_briefing": self.config["rate_limits"]["reporting_per_hour"]
        }
        self.rate_limiter = RateLimiter(rate_limits)

        # Initialize Odoo client
        try:
            self.odoo_client = OdooClient()
            self.odoo_client.authenticate()
            logger.info("Odoo client initialized and authenticated")
        except Exception as e:
            logger.error(f"Failed to initialize Odoo client: {e}")
            self.odoo_client = None

        # Initialize MCP server
        if Server is None:
            logger.error("MCP SDK not available. Server cannot start.")
            self.server = None
        else:
            self.server = Server(self.server_name)
            self._register_handlers()
            self._register_tools()

        logger.info(f"MCP Server initialized: {self.server_name} v{self.version}")

    def _register_handlers(self):
        """Register MCP protocol handlers."""
        if self.server is None:
            return

        # Register list_tools handler
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="send_email",
                    description="Send an email via SMTP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email address"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "cc": {"type": "string", "description": "CC recipients (optional)"},
                            "bcc": {"type": "string", "description": "BCC recipients (optional)"},
                            "content_type": {"type": "string", "description": "Content type (default: text/plain)"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="post_facebook_page",
                    description="Post to a Facebook Page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Post message"},
                            "link": {"type": "string", "description": "Optional link to include"},
                            "published": {"type": "boolean", "description": "Whether to publish immediately (default: true)"}
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="post_twitter",
                    description="Post a message to Twitter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Tweet text (max 280 characters)"},
                            "media_urls": {"type": "array", "items": {"type": "string"}, "description": "Optional media URLs"}
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="post_instagram",
                    description="Post to Instagram",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Post caption"},
                            "image_url": {"type": "string", "description": "Image URL (required for Instagram)"}
                        },
                        "required": ["message", "image_url"]
                    }
                ),
                Tool(
                    name="generate_ceo_briefing",
                    description="Generate weekly CEO briefing report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "week_offset": {"type": "integer", "description": "Week offset (0=current, -1=last week, default: 0)"}
                        }
                    }
                ),
                Tool(
                    name="odoo_create_customer",
                    description="Create a new customer in Odoo CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Customer name"},
                            "email": {"type": "string", "description": "Customer email"},
                            "phone": {"type": "string", "description": "Customer phone number"},
                            "street": {"type": "string", "description": "Street address"},
                            "city": {"type": "string", "description": "City"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="odoo_create_lead",
                    description="Create a new lead/opportunity in Odoo CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Lead title"},
                            "partner_id": {"type": "integer", "description": "Customer ID (optional)"},
                            "email": {"type": "string", "description": "Contact email"},
                            "phone": {"type": "string", "description": "Contact phone"},
                            "description": {"type": "string", "description": "Lead description"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="odoo_search_customer",
                    description="Search for a customer in Odoo by email or name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Customer email"},
                            "name": {"type": "string", "description": "Customer name"}
                        }
                    }
                ),
                Tool(
                    name="odoo_get_invoices",
                    description="Get invoices from Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "partner_id": {"type": "integer", "description": "Filter by customer ID"},
                            "state": {"type": "string", "description": "Filter by state (draft, posted, cancel)"},
                            "limit": {"type": "integer", "description": "Maximum number of records (default: 100)"}
                        }
                    }
                )
            ]

    def _register_tools(self):
        """Register MCP tools (functions)."""
        if self.server is None:
            return

        # Register unified tool handler that routes based on tool name
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
            """
            Handle tool calls and route to appropriate handler.

            Args:
                name: Tool name
                arguments: Tool-specific arguments

            Returns:
                List of TextContent with result
            """
            logger.info(f"Tool call received: {name}")

            # Route to appropriate handler
            handlers = {
                "send_email": self._handle_send_email,
                "post_facebook_page": self._handle_post_facebook_page,
                "post_twitter": self._handle_post_twitter,
                "post_instagram": self._handle_post_instagram,
                "generate_ceo_briefing": self._handle_generate_ceo_briefing,
                "odoo_create_customer": self._handle_odoo_create_customer,
                "odoo_create_lead": self._handle_odoo_create_lead,
                "odoo_search_customer": self._handle_odoo_search_customer,
                "odoo_get_invoices": self._handle_odoo_get_invoices
            }

            handler = handlers.get(name)
            if handler:
                return await handler(arguments)
            else:
                logger.error(f"Unknown tool: {name}")
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "UNKNOWN_TOOL",
                    "message": f"Tool '{name}' not found",
                    "timestamp": datetime.now().isoformat()
                }))]

        logger.info("MCP tools registered: send_email, post_facebook_page, post_twitter, post_instagram, generate_ceo_briefing")

    async def _handle_send_email(self, arguments: dict) -> list[TextContent]:
        """
        Handle send_email function call.

        Args:
            arguments: Email parameters

        Returns:
            Result as TextContent list
        """
        function_name = "send_email"

        logger.info(f"_handle_send_email called with arguments: {arguments}")

        # Check rate limit
        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            error_msg = f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}"
            logger.warning(f"{function_name} rate limit exceeded")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }))]

        # Record call
        self.rate_limiter.record_call(function_name)

        # Log request
        logger.info(f"{function_name} called with to={arguments.get('to')}, subject={arguments.get('subject')}")

        # Import email handler
        try:
            from mcp_server.email_handler import EmailHandler
            email_handler = EmailHandler()
        except Exception as e:
            logger.error(f"Failed to initialize email handler: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "HANDLER_INITIALIZATION_ERROR",
                "message": f"Failed to initialize email handler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))]

        # Send email
        try:
            result = email_handler.send_email(
                to=arguments.get('to'),
                subject=arguments.get('subject'),
                body=arguments.get('body'),
                cc=arguments.get('cc'),
                bcc=arguments.get('bcc'),
                content_type=arguments.get('content_type', 'text/plain')
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Email sending failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "EMAIL_SEND_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_post_facebook_page(self, arguments: dict) -> list[TextContent]:
        """
        Handle post_facebook_page function call.

        Args:
            arguments: Facebook post parameters

        Returns:
            Result as TextContent list
        """
        function_name = "post_facebook_page"

        logger.info(f"_handle_post_facebook_page called with arguments: {arguments}")

        # Check rate limit
        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            error_msg = f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}"
            logger.warning(f"{function_name} rate limit exceeded")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }))]

        # Record call
        self.rate_limiter.record_call(function_name)

        # Log request
        message_preview = arguments.get('message', '')[:50]
        logger.info(f"{function_name} called with message={message_preview}...")

        # Import Facebook handler
        try:
            from mcp_server.facebook_handler import FacebookHandler
            facebook_handler = FacebookHandler()
        except Exception as e:
            logger.error(f"Failed to initialize Facebook handler: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "HANDLER_INITIALIZATION_ERROR",
                "message": f"Failed to initialize Facebook handler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))]

        # Post to Facebook
        try:
            result = facebook_handler.post_facebook_page(
                message=arguments.get('message'),
                link=arguments.get('link'),
                published=arguments.get('published', True)
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Facebook posting failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "FACEBOOK_POST_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_post_twitter(self, arguments: dict) -> list[TextContent]:
        """Handle post_twitter function call."""
        function_name = "post_twitter"
        logger.info(f"_handle_post_twitter called with arguments: {arguments}")

        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}",
                "timestamp": datetime.now().isoformat()
            }))]

        self.rate_limiter.record_call(function_name)

        try:
            from mcp_server.twitter_handler import TwitterHandler
            handler = TwitterHandler()
            result = handler.post_twitter(
                message=arguments.get('message'),
                media_urls=arguments.get('media_urls')
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Twitter posting failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "TWITTER_POST_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_post_instagram(self, arguments: dict) -> list[TextContent]:
        """Handle post_instagram function call."""
        function_name = "post_instagram"
        logger.info(f"_handle_post_instagram called with arguments: {arguments}")

        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}",
                "timestamp": datetime.now().isoformat()
            }))]

        self.rate_limiter.record_call(function_name)

        try:
            from mcp_server.instagram_handler import InstagramHandler
            handler = InstagramHandler()
            result = handler.post_instagram(
                message=arguments.get('message'),
                image_url=arguments.get('image_url')
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Instagram posting failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "INSTAGRAM_POST_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_generate_ceo_briefing(self, arguments: dict) -> list[TextContent]:
        """Handle generate_ceo_briefing function call."""
        function_name = "generate_ceo_briefing"
        logger.info(f"_handle_generate_ceo_briefing called with arguments: {arguments}")

        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}",
                "timestamp": datetime.now().isoformat()
            }))]

        self.rate_limiter.record_call(function_name)

        try:
            from reporting.ceo_briefing import CEOBriefingGenerator
            generator = CEOBriefingGenerator()
            result = generator.generate_briefing(
                week_offset=arguments.get('week_offset', 0)
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"CEO briefing generation failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "CEO_BRIEFING_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_odoo_create_customer(self, arguments: dict) -> list[TextContent]:
        """Handle odoo_create_customer function call."""
        logger.info(f"_handle_odoo_create_customer called with arguments: {arguments}")

        if self.odoo_client is None:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_NOT_AVAILABLE",
                "message": "Odoo client not initialized",
                "timestamp": datetime.now().isoformat()
            }))]

        try:
            customer_id = self.odoo_client.create_customer(
                name=arguments.get('name'),
                email=arguments.get('email'),
                phone=arguments.get('phone'),
                street=arguments.get('street'),
                city=arguments.get('city')
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "customer_id": customer_id,
                "message": f"Customer created successfully with ID: {customer_id}",
                "timestamp": datetime.now().isoformat()
            }))]
        except Exception as e:
            logger.error(f"Odoo create customer failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_CREATE_CUSTOMER_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_odoo_create_lead(self, arguments: dict) -> list[TextContent]:
        """Handle odoo_create_lead function call."""
        logger.info(f"_handle_odoo_create_lead called with arguments: {arguments}")

        if self.odoo_client is None:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_NOT_AVAILABLE",
                "message": "Odoo client not initialized",
                "timestamp": datetime.now().isoformat()
            }))]

        try:
            lead_id = self.odoo_client.create_lead(
                name=arguments.get('name'),
                partner_id=arguments.get('partner_id'),
                email=arguments.get('email'),
                phone=arguments.get('phone'),
                description=arguments.get('description')
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "lead_id": lead_id,
                "message": f"Lead created successfully with ID: {lead_id}",
                "timestamp": datetime.now().isoformat()
            }))]
        except Exception as e:
            logger.error(f"Odoo create lead failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_CREATE_LEAD_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_odoo_search_customer(self, arguments: dict) -> list[TextContent]:
        """Handle odoo_search_customer function call."""
        logger.info(f"_handle_odoo_search_customer called with arguments: {arguments}")

        if self.odoo_client is None:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_NOT_AVAILABLE",
                "message": "Odoo client not initialized",
                "timestamp": datetime.now().isoformat()
            }))]

        try:
            customer_id = self.odoo_client.search_customer(
                email=arguments.get('email'),
                name=arguments.get('name')
            )
            if customer_id:
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "customer_id": customer_id,
                    "message": f"Customer found with ID: {customer_id}",
                    "timestamp": datetime.now().isoformat()
                }))]
            else:
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "customer_id": None,
                    "message": "No customer found matching criteria",
                    "timestamp": datetime.now().isoformat()
                }))]
        except Exception as e:
            logger.error(f"Odoo search customer failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_SEARCH_CUSTOMER_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_odoo_get_invoices(self, arguments: dict) -> list[TextContent]:
        """Handle odoo_get_invoices function call."""
        logger.info(f"_handle_odoo_get_invoices called with arguments: {arguments}")

        if self.odoo_client is None:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_NOT_AVAILABLE",
                "message": "Odoo client not initialized",
                "timestamp": datetime.now().isoformat()
            }))]

        try:
            invoices = self.odoo_client.get_invoices(
                partner_id=arguments.get('partner_id'),
                state=arguments.get('state'),
                limit=arguments.get('limit', 100)
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "invoices": invoices,
                "count": len(invoices),
                "message": f"Retrieved {len(invoices)} invoices",
                "timestamp": datetime.now().isoformat()
            }))]
        except Exception as e:
            logger.error(f"Odoo get invoices failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "ODOO_GET_INVOICES_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def run(self):
        """Run the MCP server."""
        if self.server is None:
            logger.error("Cannot run server: MCP SDK not available")
            return

        logger.info(f"Starting MCP server: {self.server_name}")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for MCP server."""
    import asyncio

    try:
        server = GoldTierMCPServer()
        asyncio.run(server.run())
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
