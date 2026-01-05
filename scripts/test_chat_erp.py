from app.services.chat_service import handle_chat_message
from app.db.schemas.chat_schema import ChatRequest
from app.erp_tools.modules.sales_crm.tools import (
    get_order_status,
    check_voucher_valid,
    get_customer_profile
)

def test(question: str):
    req = ChatRequest(
        question=question,
        session_id="demo_session"
    )
    res = handle_chat_message(req)
    print("\nQUESTION:", question)
    print("ANSWER:", res.answer)

if __name__ == "__main__":
    test("Mã SALE10 có dùng được không?")
    test("Đơn hàng 1 đã giao chưa?")
    test("Cho tôi hỏi chi tiết về đơn hàng 1.")
    test("Tôi đã mua những gì?")
    test("Thông tin tài khoản của tôi")
