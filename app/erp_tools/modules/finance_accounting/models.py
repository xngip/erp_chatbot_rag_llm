# app/db/finance_models.py
from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, DateTime,
    Numeric, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.finance_database import FinanceBase


# =========================
# 1. BUSINESS PARTNERS
# =========================
class BusinessPartner(FinanceBase):
    __tablename__ = "business_partners"

    partner_id = Column(Integer, primary_key=True)
    partner_type = Column(Enum("CUSTOMER", "SUPPLIER", name="partner_type_enum"))
    external_id = Column(String(50))
    partner_name = Column(String(255))
    tax_code = Column(String(50))
    contact_info = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# =========================
# 2. FISCAL PERIODS
# =========================
class FiscalPeriod(FinanceBase):
    __tablename__ = "fiscal_periods"

    period_id = Column(Integer, primary_key=True)
    period_name = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum("OPEN", "CLOSED", name="fiscal_status_enum"))

    closed_at = Column(DateTime)
    closed_by_user_id = Column(String(50))


# =========================
# 3. JOURNAL ENTRIES
# =========================
class JournalEntry(FinanceBase):
    __tablename__ = "journal_entries"

    entry_id = Column(BigInteger, primary_key=True)
    transaction_date = Column(Date)
    posting_date = Column(DateTime)
    reference_no = Column(String(50))
    description = Column(String)

    source_module = Column(Enum(
        "AR", "AP", "CASH", "MANUAL",
        name="source_module_enum"
    ))

    status = Column(Enum("DRAFT", "POSTED", name="journal_status_enum"))

    fiscal_period_id = Column(Integer, ForeignKey("fiscal_periods.period_id"))
    total_amount = Column(Numeric(19, 4))

    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    fiscal_period = relationship("FiscalPeriod")
    lines = relationship("JournalEntryLine", back_populates="entry")


# =========================
# 4. JOURNAL ENTRY LINES
# =========================
class JournalEntryLine(FinanceBase):
    __tablename__ = "journal_entry_lines"

    line_id = Column(BigInteger, primary_key=True)
    entry_id = Column(BigInteger, ForeignKey("journal_entries.entry_id"))
    account_id = Column(Integer, ForeignKey("chart_of_accounts.account_id"))
    partner_id = Column(Integer, ForeignKey("business_partners.partner_id"))

    debit_amount = Column(Numeric(19, 4))
    credit_amount = Column(Numeric(19, 4))
    description = Column(String(255))

    entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccount")
    partner = relationship("BusinessPartner")


# =========================
# 5. CHART OF ACCOUNTS
# =========================
class ChartOfAccount(FinanceBase):
    __tablename__ = "chart_of_accounts"

    account_id = Column(Integer, primary_key=True)
    account_code = Column(String(20), unique=True)
    account_name = Column(String(255))

    account_type = Column(Enum(
        "ASSET", "LIABILITY", "EQUITY",
        "REVENUE", "EXPENSE",
        name="account_type_enum"
    ))

    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.account_id"))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("ChartOfAccount", remote_side=[account_id])


# =========================
# 6. AR INVOICES
# =========================
class ARInvoice(FinanceBase):
    __tablename__ = "ar_invoices"

    invoice_id = Column(BigInteger, primary_key=True)
    partner_id = Column(Integer, ForeignKey("business_partners.partner_id"))

    sales_order_ref = Column(String(50))
    invoice_date = Column(Date)
    due_date = Column(Date)

    total_amount = Column(Numeric(19, 4))
    received_amount = Column(Numeric(19, 4))

    payment_status = Column(Enum(
        "UNPAID", "PARTIAL", "PAID",
        name="ar_payment_status_enum"
    ))

    entry_id = Column(BigInteger, ForeignKey("journal_entries.entry_id"))

    partner = relationship("BusinessPartner")
    entry = relationship("JournalEntry")


# =========================
# 7. AP INVOICES
# =========================
class APInvoice(FinanceBase):
    __tablename__ = "ap_invoices"

    invoice_id = Column(BigInteger, primary_key=True)
    partner_id = Column(Integer, ForeignKey("business_partners.partner_id"))

    purchase_order_ref = Column(String(50))
    invoice_date = Column(Date)
    due_date = Column(Date)

    total_amount = Column(Numeric(19, 4))
    paid_amount = Column(Numeric(19, 4))

    payment_status = Column(Enum(
        "UNPAID", "PARTIAL", "PAID",
        name="ap_payment_status_enum"
    ))

    entry_id = Column(BigInteger, ForeignKey("journal_entries.entry_id"))

    partner = relationship("BusinessPartner")
    entry = relationship("JournalEntry")


# =========================
# 8. CASH TRANSACTIONS
# =========================
class CashTransaction(FinanceBase):
    __tablename__ = "cash_transactions"

    transaction_id = Column(BigInteger, primary_key=True)
    transaction_type = Column(Enum(
        "INFLOW", "OUTFLOW",
        name="cash_transaction_type_enum"
    ))

    amount = Column(Numeric(19, 4))
    payment_method = Column(Enum(
        "CASH", "BANK_TRANSFER",
        name="payment_method_enum"
    ))

    bank_account_number = Column(String(50))
    reference_doc_id = Column(BigInteger)
    entry_id = Column(BigInteger, ForeignKey("journal_entries.entry_id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    entry = relationship("JournalEntry")


# =========================
# 9. POSTING RULES
# =========================
class PostingRule(FinanceBase):
    __tablename__ = "posting_rules"

    rule_id = Column(Integer, primary_key=True)
    event_code = Column(String(50))
    event_description = Column(String(255))

    debit_account_id = Column(Integer, ForeignKey("chart_of_accounts.account_id"))
    credit_account_id = Column(Integer, ForeignKey("chart_of_accounts.account_id"))

    module_source = Column(Enum(
        "AR", "AP", "CASH",
        name="posting_module_enum"
    ))

    debit_account = relationship(
        "ChartOfAccount",
        foreign_keys=[debit_account_id]
    )
    credit_account = relationship(
        "ChartOfAccount",
        foreign_keys=[credit_account_id]
    )
