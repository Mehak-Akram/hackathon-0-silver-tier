"""
Financial Transaction model for Gold Tier Autonomous AI Employee.

Represents a financial event from an accounting system.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class TransactionType(str, Enum):
    """Financial transaction types."""
    REVENUE = "revenue"
    EXPENSE = "expense"
    INVOICE = "invoice"
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, Enum):
    """Transaction status."""
    DRAFT = "draft"
    POSTED = "posted"
    PAID = "paid"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PaymentMethod(str, Enum):
    """Payment methods."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    ONLINE = "online"
    OTHER = "other"


class FinancialTransaction(BaseModel):
    """
    Financial Transaction entity representing a financial event from an accounting system.

    Attributes:
        transaction_id: Unique transaction identifier
        external_id: External system ID (e.g., accounting system invoice ID)
        transaction_type: Type of transaction
        status: Transaction status

        transaction_date: Date of transaction
        due_date: Payment due date (for invoices)
        paid_date: Date payment was received

        amount: Transaction amount
        currency: Currency code (e.g., "USD")
        tax_amount: Tax amount
        total_amount: Total amount including tax

        category: Transaction category (e.g., "consulting", "software")
        description: Transaction description

        customer_id: Customer identifier
        customer_name: Customer name
        vendor_id: Vendor identifier (for expenses)
        vendor_name: Vendor name

        invoice_reference: Invoice reference number
        payment_method: How payment was made
        payment_reference: Payment reference/transaction ID

        account_code: Accounting account code
        cost_center: Cost center or department

        metadata: Additional transaction metadata
    """

    transaction_id: str = Field(..., description="Unique transaction identifier")
    external_id: Optional[str] = Field(default=None, description="External system ID")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    status: TransactionStatus = Field(default=TransactionStatus.DRAFT, description="Transaction status")

    # Dates
    transaction_date: date = Field(..., description="Transaction date")
    due_date: Optional[date] = Field(default=None, description="Due date")
    paid_date: Optional[date] = Field(default=None, description="Paid date")

    # Amounts
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    tax_amount: Decimal = Field(default=Decimal("0.00"), description="Tax amount")
    total_amount: Decimal = Field(..., description="Total amount")

    # Description
    category: Optional[str] = Field(default=None, description="Transaction category")
    description: str = Field(..., description="Transaction description")

    # Parties
    customer_id: Optional[str] = Field(default=None, description="Customer ID")
    customer_name: Optional[str] = Field(default=None, description="Customer name")
    vendor_id: Optional[str] = Field(default=None, description="Vendor ID")
    vendor_name: Optional[str] = Field(default=None, description="Vendor name")

    # References
    invoice_reference: Optional[str] = Field(default=None, description="Invoice reference")
    payment_method: Optional[PaymentMethod] = Field(default=None, description="Payment method")
    payment_reference: Optional[str] = Field(default=None, description="Payment reference")

    # Accounting
    account_code: Optional[str] = Field(default=None, description="Account code")
    cost_center: Optional[str] = Field(default=None, description="Cost center")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v)
        }
        use_enum_values = True

    def mark_posted(self) -> None:
        """Mark transaction as posted."""
        self.status = TransactionStatus.POSTED

    def mark_paid(self, paid_date: Optional[date] = None, payment_method: Optional[PaymentMethod] = None) -> None:
        """
        Mark transaction as paid.

        Args:
            paid_date: Date payment was received
            payment_method: Payment method used
        """
        self.status = TransactionStatus.PAID
        self.paid_date = paid_date or date.today()
        if payment_method:
            self.payment_method = payment_method

    def mark_cancelled(self) -> None:
        """Mark transaction as cancelled."""
        self.status = TransactionStatus.CANCELLED

    def is_overdue(self) -> bool:
        """
        Check if transaction is overdue.

        Returns:
            True if transaction is overdue
        """
        if not self.due_date or self.status == TransactionStatus.PAID:
            return False
        return date.today() > self.due_date

    def days_overdue(self) -> int:
        """
        Calculate days overdue.

        Returns:
            Number of days overdue (0 if not overdue)
        """
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days

    def is_revenue(self) -> bool:
        """Check if transaction is revenue."""
        return self.transaction_type in [TransactionType.REVENUE, TransactionType.INVOICE]

    def is_expense(self) -> bool:
        """Check if transaction is expense."""
        return self.transaction_type == TransactionType.EXPENSE

    def calculate_total(self) -> Decimal:
        """
        Calculate total amount (amount + tax).

        Returns:
            Total amount
        """
        return self.amount + self.tax_amount

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert transaction to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialTransaction":
        """
        Create transaction from dictionary.

        Args:
            data: Transaction data dictionary

        Returns:
            FinancialTransaction instance
        """
        # Convert string amounts to Decimal
        if "amount" in data and isinstance(data["amount"], (int, float, str)):
            data["amount"] = Decimal(str(data["amount"]))
        if "tax_amount" in data and isinstance(data["tax_amount"], (int, float, str)):
            data["tax_amount"] = Decimal(str(data["tax_amount"]))
        if "total_amount" in data and isinstance(data["total_amount"], (int, float, str)):
            data["total_amount"] = Decimal(str(data["total_amount"]))

        return cls(**data)

    @classmethod
    def from_invoice_data(cls, invoice_data: Dict[str, Any]) -> "FinancialTransaction":
        """
        Create transaction from invoice data.

        Args:
            invoice_data: Invoice data from accounting system

        Returns:
            FinancialTransaction instance
        """
        return cls(
            transaction_id=f"inv_{invoice_data.get('id')}",
            external_id=str(invoice_data.get('id')),
            transaction_type=TransactionType.INVOICE,
            status=TransactionStatus.POSTED if invoice_data.get('state') == 'posted' else TransactionStatus.DRAFT,
            transaction_date=datetime.strptime(invoice_data.get('invoice_date', str(date.today())), '%Y-%m-%d').date(),
            amount=Decimal(str(invoice_data.get('amount_untaxed', 0))),
            tax_amount=Decimal(str(invoice_data.get('amount_tax', 0))),
            total_amount=Decimal(str(invoice_data.get('amount_total', 0))),
            description=invoice_data.get('name', 'Invoice'),
            customer_id=str(invoice_data.get('partner_id', [None])[0]) if isinstance(invoice_data.get('partner_id'), list) else None,
            customer_name=invoice_data.get('partner_id', [None, ''])[1] if isinstance(invoice_data.get('partner_id'), list) else None,
            invoice_reference=invoice_data.get('name'),
            currency=invoice_data.get('currency_id', [None, 'USD'])[1] if isinstance(invoice_data.get('currency_id'), list) else 'USD'
        )
