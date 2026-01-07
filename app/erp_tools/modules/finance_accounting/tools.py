from datetime import date
from sqlalchemy import func
from app.db.finance_database import FinanceSessionLocal

from app.erp_tools.modules.finance_accounting.models import (
    BusinessPartner,
    ARInvoice,
    APInvoice,
    CashTransaction,
    JournalEntry,
    JournalEntryLine,
    ChartOfAccounts,
    FiscalPeriod,
    PostingRule
)

def get_ar_invoice_status(invoice_id: int):
    db = FinanceSessionLocal()
    try:
        inv = db.query(ARInvoice).filter(ARInvoice.invoice_id == invoice_id).first()
        if not inv:
            return {"message": "Không tìm thấy hóa đơn bán"}

        return {
            "invoice_id": inv.invoice_id,
            "total_amount": float(inv.total_amount),
            "received_amount": float(inv.received_amount),
            "payment_status": inv.payment_status,
            "due_date": inv.due_date
        }
    finally:
        db.close()

def get_ar_invoice_detail(invoice_id: int):
    db = FinanceSessionLocal()
    try:
        inv = (
            db.query(ARInvoice, BusinessPartner)
            .join(BusinessPartner, ARInvoice.partner_id == BusinessPartner.partner_id)
            .filter(ARInvoice.invoice_id == invoice_id)
            .first()
        )
        if not inv:
            return None

        ar, partner = inv
        return {
            "invoice_id": ar.invoice_id,
            "customer": partner.partner_name,
            "invoice_date": ar.invoice_date,
            "due_date": ar.due_date,
            "total_amount": float(ar.total_amount),
            "received_amount": float(ar.received_amount),
            "payment_status": ar.payment_status
        }
    finally:
        db.close()

def get_customer_receivable_summary(partner_id: int):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(
                func.sum(ARInvoice.total_amount),
                func.sum(ARInvoice.received_amount)
            )
            .filter(ARInvoice.partner_id == partner_id)
            .first()
        )

        total, received = rows
        return {
            "partner_id": partner_id,
            "total_receivable": float(total or 0),
            "total_received": float(received or 0),
            "outstanding": float((total or 0) - (received or 0))
        }
    finally:
        db.close()

def get_ap_invoice_status(invoice_id: int):
    db = FinanceSessionLocal()
    try:
        inv = db.query(APInvoice).filter(APInvoice.invoice_id == invoice_id).first()
        if not inv:
            return {"message": "Không tìm thấy hóa đơn mua"}

        return {
            "invoice_id": inv.invoice_id,
            "total_amount": float(inv.total_amount),
            "paid_amount": float(inv.paid_amount),
            "payment_status": inv.payment_status,
            "due_date": inv.due_date
        }
    finally:
        db.close()

def get_ap_invoice_detail(invoice_id: int):
    db = FinanceSessionLocal()
    try:
        inv = (
            db.query(APInvoice, BusinessPartner)
            .join(BusinessPartner, APInvoice.partner_id == BusinessPartner.partner_id)
            .filter(APInvoice.invoice_id == invoice_id)
            .first()
        )
        if not inv:
            return None

        ap, supplier = inv
        return {
            "invoice_id": ap.invoice_id,
            "supplier": supplier.partner_name,
            "invoice_date": ap.invoice_date,
            "due_date": ap.due_date,
            "total_amount": float(ap.total_amount),
            "paid_amount": float(ap.paid_amount),
            "payment_status": ap.payment_status
        }
    finally:
        db.close()

def get_supplier_payable_summary(partner_id: int):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(
                func.sum(APInvoice.total_amount),
                func.sum(APInvoice.paid_amount)
            )
            .filter(APInvoice.partner_id == partner_id)
            .first()
        )

        total, paid = rows
        return {
            "partner_id": partner_id,
            "total_payable": float(total or 0),
            "total_paid": float(paid or 0),
            "outstanding": float((total or 0) - (paid or 0))
        }
    finally:
        db.close()

def get_cash_transaction(transaction_id: int):
    db = FinanceSessionLocal()
    try:
        tx = db.query(CashTransaction).filter(CashTransaction.transaction_id == transaction_id).first()
        if not tx:
            return None

        return {
            "transaction_type": tx.transaction_type,
            "amount": float(tx.amount),
            "payment_method": tx.payment_method,
            "bank_account": tx.bank_account_number,
            "created_at": tx.created_at
        }
    finally:
        db.close()

def get_journal_entries(limit: int = 10):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(JournalEntry)
            .order_by(JournalEntry.transaction_date.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "entry_id": e.entry_id,
                "date": e.transaction_date,
                "description": e.description,
                "total_amount": float(e.total_amount),
                "status": e.status
            }
            for e in rows
        ]
    finally:
        db.close()

def get_journal_entry_detail(entry_id: int):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(JournalEntryLine, ChartOfAccounts)
            .join(ChartOfAccounts, JournalEntryLine.account_id == ChartOfAccounts.account_id)
            .filter(JournalEntryLine.entry_id == entry_id)
            .all()
        )

        return [
            {
                "account": acc.account_name,
                "debit": float(line.debit_amount),
                "credit": float(line.credit_amount)
            }
            for line, acc in rows
        ]
    finally:
        db.close()

def get_account_balance(account_id: int):
    db = FinanceSessionLocal()
    try:
        debit, credit = db.query(
            func.sum(JournalEntryLine.debit_amount),
            func.sum(JournalEntryLine.credit_amount)
        ).filter(JournalEntryLine.account_id == account_id).first()

        return {
            "account_id": account_id,
            "balance": float((debit or 0) - (credit or 0))
        }
    finally:
        db.close()

def get_current_fiscal_period():
    db = FinanceSessionLocal()
    try:
        p = db.query(FiscalPeriod).filter(FiscalPeriod.status == "OPEN").first()
        if not p:
            return {"message": "Không có kỳ kế toán đang mở"}

        return {
            "period_name": p.period_name,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "status": p.status
        }
    finally:
        db.close()

def get_fiscal_periods(limit: int = 6):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(FiscalPeriod)
            .order_by(FiscalPeriod.start_date.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "period": r.period_name,
                "status": r.status
            }
            for r in rows
        ]
    finally:
        db.close()

def explain_posting_rule(event_code: str):
    db = FinanceSessionLocal()
    try:
        r = db.query(PostingRule).filter(PostingRule.event_code == event_code).first()
        if not r:
            return {"message": "Không tìm thấy rule hạch toán"}

        return {
            "event": r.event_code,
            "description": r.event_description,
            "debit_account_id": r.debit_account_id,
            "credit_account_id": r.credit_account_id,
            "module": r.module_source
        }
    finally:
        db.close()

def get_cash_flow_history(limit: int = 10):
    db = FinanceSessionLocal()
    try:
        rows = (
            db.query(CashTransaction)
            .order_by(CashTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "type": r.transaction_type,
                "amount": float(r.amount),
                "method": r.payment_method,
                "date": r.created_at
            }
            for r in rows
        ]
    finally:
        db.close()
