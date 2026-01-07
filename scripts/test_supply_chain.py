import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.services.chat_supply_chain import handle_chat_supply_chain
from app.db.schemas.chat_schema import ChatRequest


questions = [
    # 1️⃣ PROCUREMENT – multi-tool (bạn đã test)
    "Đơn mua PO-001 đã nhập bao nhiêu % và còn thiếu gì?",

    # 2️⃣ INVENTORY – tồn kho + cảnh báo
    "Sản phẩm 1 còn hàng không?",

    # 3️⃣ INVENTORY – tổng tồn theo kho
    "Kho Hà Nội hiện còn bao nhiêu laptop Dell?",

    # 4️⃣ PROCUREMENT – trạng thái đơn mua
    "Nhà cung cấp FPT có giao hàng đúng hạn không?",

    # 5️⃣ INVENTORY AUDIT – truy vết biến động
    "Lịch sử biến động tồn kho của sản phẩm 1 là gì?"
]

for i, q in enumerate(questions, start=1):
    req = ChatRequest(
        session_id=f"test_sc_{i}",
        question=q
    )
    print(f"\n🟢 Câu hỏi {i}: {q}")
    print("➡️ Trả lời:")
    print(handle_chat_supply_chain(req).answer)
