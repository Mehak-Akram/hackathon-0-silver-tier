"""
Odoo Client - XML-RPC Integration Layer
Provides clean interface for AI system to interact with Odoo ERP
"""

import xmlrpc.client
import logging
from typing import Dict, List, Optional, Any
from functools import wraps
import os

logger = logging.getLogger(__name__)


class OdooConnectionError(Exception):
    """Raised when connection to Odoo fails"""
    pass


class OdooAuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class OdooOperationError(Exception):
    """Raised when an Odoo operation fails"""
    pass


def handle_odoo_errors(func):
    """Decorator to handle common Odoo errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except xmlrpc.client.Fault as e:
            logger.error(f"Odoo XML-RPC Fault in {func.__name__}: {e}")
            raise OdooOperationError(f"Odoo operation failed: {e.faultString}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper


class OdooClient:
    """
    Odoo XML-RPC Client for external API integration

    Usage:
        client = OdooClient()
        client.authenticate()
        customer_id = client.create_customer("John Doe", "john@example.com")
    """

    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Odoo client with connection parameters

        Args:
            url: Odoo server URL (default: from ODOO_URL env)
            db: Database name (default: from ODOO_DB env)
            username: Odoo username (default: from ODOO_USERNAME env)
            password: Odoo password (default: from ODOO_PASSWORD env)
        """
        self.url = url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = db or os.getenv('ODOO_DB', 'odoo_db')
        self.username = username or os.getenv('ODOO_USERNAME', 'admin@example.com')
        self.password = password or os.getenv('ODOO_PASSWORD', 'odoo')

        self.uid: Optional[int] = None
        self.common: Optional[xmlrpc.client.ServerProxy] = None
        self.models: Optional[xmlrpc.client.ServerProxy] = None

        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize XML-RPC connections"""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            logger.info(f"Initialized Odoo connection to {self.url}")
        except Exception as e:
            logger.error(f"Failed to initialize Odoo connections: {e}")
            raise OdooConnectionError(f"Cannot connect to Odoo at {self.url}: {e}")

    def authenticate(self) -> int:
        """
        Authenticate with Odoo server

        Returns:
            User ID (uid) if successful

        Raises:
            OdooAuthenticationError: If authentication fails
        """
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                raise OdooAuthenticationError("Authentication failed - invalid credentials")
            logger.info(f"Authenticated as user ID: {self.uid}")
            return self.uid
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise OdooAuthenticationError(f"Failed to authenticate: {e}")

    def _execute(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """
        Execute Odoo model method

        Args:
            model: Odoo model name (e.g., 'res.partner')
            method: Method name (e.g., 'create', 'search', 'read')
            args: List of positional arguments for the method
            kwargs: Dict of keyword arguments for the method
        """
        if not self.uid:
            raise OdooAuthenticationError("Not authenticated - call authenticate() first")

        if kwargs is None:
            kwargs = {}

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )

    @handle_odoo_errors
    def create_customer(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        country_code: Optional[str] = None,
        **extra_fields
    ) -> int:
        """
        Create a new customer (contact) in Odoo

        Args:
            name: Customer name (required)
            email: Email address
            phone: Phone number
            mobile: Mobile number
            street: Street address
            city: City
            country_code: ISO country code (e.g., 'US', 'GB')
            **extra_fields: Additional fields to set

        Returns:
            Customer ID (partner_id)
        """
        values = {
            'name': name,
            'customer_rank': 1,  # Mark as customer
        }

        if email:
            values['email'] = email
        if phone:
            values['phone'] = phone
        if mobile:
            values['mobile'] = mobile
        if street:
            values['street'] = street
        if city:
            values['city'] = city
        if country_code:
            # Find country by code
            country_ids = self._execute('res.country', 'search', [[('code', '=', country_code)]], {})
            if country_ids:
                values['country_id'] = country_ids[0]

        values.update(extra_fields)

        customer_id = self._execute('res.partner', 'create', [values])
        logger.info(f"Created customer: {name} (ID: {customer_id})")
        return customer_id

    @handle_odoo_errors
    def create_lead(
        self,
        name: str,
        partner_id: Optional[int] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        **extra_fields
    ) -> int:
        """
        Create a new lead/opportunity in CRM

        Args:
            name: Lead title (required)
            partner_id: Existing customer ID (optional)
            email: Contact email
            phone: Contact phone
            description: Lead description/notes
            **extra_fields: Additional fields

        Returns:
            Lead ID
        """
        values = {
            'name': name,
            'type': 'opportunity',
        }

        if partner_id:
            values['partner_id'] = partner_id
        if email:
            values['email_from'] = email
        if phone:
            values['phone'] = phone
        if description:
            values['description'] = description

        values.update(extra_fields)

        lead_id = self._execute('crm.lead', 'create', [values])
        logger.info(f"Created lead: {name} (ID: {lead_id})")
        return lead_id

    @handle_odoo_errors
    def create_sale_order(
        self,
        partner_id: int,
        order_lines: List[Dict[str, Any]],
        **extra_fields
    ) -> int:
        """
        Create a sales order

        Args:
            partner_id: Customer ID (required)
            order_lines: List of order line dicts with keys:
                - product_id: Product ID
                - product_uom_qty: Quantity
                - price_unit: Unit price (optional)
            **extra_fields: Additional fields

        Returns:
            Sale order ID
        """
        lines = []
        for line in order_lines:
            lines.append((0, 0, {
                'product_id': line['product_id'],
                'product_uom_qty': line.get('product_uom_qty', 1),
                'price_unit': line.get('price_unit'),
            }))

        values = {
            'partner_id': partner_id,
            'order_line': lines,
        }
        values.update(extra_fields)

        order_id = self._execute('sale.order', 'create', [values])
        logger.info(f"Created sale order for partner {partner_id} (ID: {order_id})")
        return order_id

    @handle_odoo_errors
    def get_invoices(
        self,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get invoices with optional filters

        Args:
            partner_id: Filter by customer ID
            state: Filter by state ('draft', 'posted', 'cancel')
            limit: Maximum number of records

        Returns:
            List of invoice records
        """
        domain = [('move_type', '=', 'out_invoice')]

        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if state:
            domain.append(('state', '=', state))

        invoice_ids = self._execute('account.move', 'search', [domain], {'limit': limit})

        if not invoice_ids:
            return []

        invoices = self._execute('account.move', 'read', [invoice_ids], {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date']})
        logger.info(f"Retrieved {len(invoices)} invoices")
        return invoices

    @handle_odoo_errors
    def search_customer(self, email: Optional[str] = None, name: Optional[str] = None) -> Optional[int]:
        """
        Search for existing customer by email or name

        Args:
            email: Customer email
            name: Customer name

        Returns:
            Customer ID if found, None otherwise
        """
        domain = []
        if email:
            domain.append(('email', '=', email))
        if name:
            domain.append(('name', 'ilike', name))

        if not domain:
            return None

        partner_ids = self._execute('res.partner', 'search', [domain], {'limit': 1})
        return partner_ids[0] if partner_ids else None

    def test_connection(self) -> bool:
        """
        Test connection and authentication

        Returns:
            True if connection successful
        """
        try:
            version = self.common.version()
            logger.info(f"Connected to Odoo version: {version}")
            self.authenticate()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
