# scripts/test_chat_finance.py

import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.services.chat_finance import handle_chat_finance
from app.db.schemas.chat_schema import ChatRequest


def run_test():
    session_id = "test_finance_001"

    questions = [
        # ===== HÓA ĐƠN BÁN (AR) =====
        "Hóa đơn bán AR-001 đã thu tiền chưa?",

        # ===== CÔNG NỢ KHÁCH HÀNG =====
        "Khách hàng A còn nợ bao nhiêu?",

        # ===== HÓA ĐƠN MUA (AP) =====
        "Hóa đơn mua AP-009 đã thanh toán chưa?",

        # ===== THU – CHI =====
        "Hôm nay có giao dịch thu chi nào?",

        # ===== KỲ KẾ TOÁN =====
        "Kỳ kế toán hiện tại là tháng nào?"
    ]

    for q in questions:
        print("=" * 80)
        print("QUESTION:", q)

        req = ChatRequest(
            session_id=session_id,
            question=q
        )

        res = handle_chat_finance(req)

        print("ANSWER:", res.answer)
        print("TYPE:", res.response_type)


if __name__ == "__main__":
    run_test()
