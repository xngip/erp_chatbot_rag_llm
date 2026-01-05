# scripts/test_chat_sale_crm.py

import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.services.chat_sale_crm import handle_chat_sale_crm
from app.db.schemas.chat_schema import ChatRequest

def run_test():
    session_id = "test_sale_crm_001"

    questions = [
        "Đơn hàng 1 đã giao chưa?",
        # "Cho tôi xem chi tiết đơn hàng 1",
        "Tôi đã mua những gì?",
        "Mã SALE10 có dùng được không?",
        # "Thông tin tài khoản của tôi",
        "Sản phẩm 1 có những phiên bản nào?"
    ]

    for q in questions:
        print("=" * 80)
        print("QUESTION:", q)

        req = ChatRequest(
            session_id=session_id,
            question=q
        )

        res = handle_chat_sale_crm(req)

        print("ANSWER:", res.answer)
        print("TYPE:", res.response_type)


if __name__ == "__main__":
    run_test()
