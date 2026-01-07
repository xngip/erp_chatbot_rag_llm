# scripts/seed_finance_data.py
import sys
import os

# Cho phép import app/*
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from datetime import date, datetime
from app.db.finance_database import FinanceSessionLocal

from app.erp_tools.modules.finance_accounting.models import (
    BusinessPartner,
    FiscalPeriod,
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    ARInvoice,
    APInvoice,
    CashTransaction,
    PostingRule
)


def seed_finance_data():
    db = FinanceSessionLocal()

    try:
        # =========================
        # 1. BUSINESS PARTNERS
        # =========================
        customer = BusinessPartner(
            partner_type="CUSTOMER",
            external_id="CUS001",
            partner_name="Công ty ABC",
            tax_code="0101234567",
            contact_info="abc@company.com"
        )

        supplier = BusinessPartner(
            partner_type="SUPPLIER",
            external_id="SUP001",
            partner_name="Nhà cung cấp XYZ",
            tax_code="0207654321",
            contact_info="xyz@supplier.com"
        )

        db.add_all([customer, supplier])
        db.commit()

        # =========================
        # 2. FISCAL PERIOD
        # =========================
        fiscal = FiscalPeriod(
            period_name="01/2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            status="OPEN"
        )
        db.add(fiscal)
        db.commit()

        # =========================
        # 3. CHART OF ACCOUNTS
        # =========================
        cash = ChartOfAccounts(
            account_code="111",
            account_name="Tiền mặt",
            account_type="ASSET"
        )

        receivable = ChartOfAccounts(
            account_code="131",
            account_name="Phải thu khách hàng",
            account_type="ASSET"
        )

        revenue = ChartOfAccounts(
            account_code="511",
            account_name="Doanh thu bán hàng",
            account_type="REVENUE"
        )

        payable = ChartOfAccounts(
            account_code="331",
            account_name="Phải trả nhà cung cấp",
            account_type="LIABILITY"
        )

        db.add_all([cash, receivable, revenue, payable])
        db.commit()

        # =========================
        # 4. JOURNAL ENTRY
        # =========================
        entry = JournalEntry(
            transaction_date=date.today(),
            posting_date=datetime.utcnow(),
            reference_no="AR001",
            description="Bán hàng cho khách ABC",
            source_module="SALES",
            status="POSTED",
            fiscal_period_id=fiscal.period_id,
            total_amount=15000000,
            created_by="system"
        )
        db.add(entry)
        db.commit()

        # =========================
        # 5. JOURNAL ENTRY LINES
        # =========================
        line1 = JournalEntryLine(
            entry_id=entry.entry_id,
            account_id=receivable.account_id,
            partner_id=customer.partner_id,
            debit_amount=15000000,
            credit_amount=0,
            description="Ghi nhận công nợ khách hàng"
        )

        line2 = JournalEntryLine(
            entry_id=entry.entry_id,
            account_id=revenue.account_id,
            partner_id=customer.partner_id,
            debit_amount=0,
            credit_amount=15000000,
            description="Doanh thu bán hàng"
        )

        db.add_all([line1, line2])
        db.commit()

        # =========================
        # 6. AR INVOICE
        # =========================
        ar = ARInvoice(
            partner_id=customer.partner_id,
            sales_order_ref="SO001",
            invoice_date=date.today(),
            due_date=date(2026, 1, 31),
            total_amount=15000000,
            received_amount=0,
            payment_status="UNPAID",
            entry_id=entry.entry_id
        )
        db.add(ar)
        db.commit()

        # =========================
        # 7. CASH TRANSACTION
        # =========================
        cash_tx = CashTransaction(
            transaction_type="RECEIPT",
            amount=5000000,
            payment_method="BANK_TRANSFER",
            bank_account_number="123-456-789",
            reference_doc_id=ar.invoice_id,
            entry_id=entry.entry_id
        )
        db.add(cash_tx)
        db.commit()

        # =========================
        # 8. POSTING RULE
        # =========================
        rule = PostingRule(
            event_code="SALE_INVOICE",
            event_description="Ghi nhận hóa đơn bán hàng",
            debit_account_id=receivable.account_id,
            credit_account_id=revenue.account_id,
            module_source="SALES"
        )
        db.add(rule)
        db.commit()

        print("✅ Seed dữ liệu Finance & Accounting thành công!")

    except Exception as e:
        db.rollback()
        print("❌ Lỗi seed finance:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_finance_data()
