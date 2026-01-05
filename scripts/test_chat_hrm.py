# scripts/test_chat_hrm.py

import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.services.chat_hrm import handle_chat_hrm
from app.db.schemas.chat_schema import ChatRequest

def run_test():
    session_id = "test_hrm_001"

    questions = [
        "Thông tin nhân viên của tôi",
        # "Tôi thuộc phòng ban nào?",
        "Chức vụ của tôi là gì?",
        "Hôm nay tôi có chấm công không?",
        "Lịch sử chấm công của tôi",
        "Lương tháng 1 năm 2026 của tôi",
        # "Chi tiết lương tháng 1 năm 2026",
        # "Lịch sử lương của tôi"
    ]

    for q in questions:
        print("=" * 80)
        print("QUESTION:", q)

        req = ChatRequest(
            session_id=session_id,
            question=q
        )

        res = handle_chat_hrm(req)

        print("ANSWER:", res.answer)
        print("TYPE:", res.response_type)


if __name__ == "__main__":
    run_test()
