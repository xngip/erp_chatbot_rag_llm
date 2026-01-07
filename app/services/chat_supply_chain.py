import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.config import settings
from app.db.database import SessionLocal
from app.db.schemas.chat_schema import ChatRequest, ChatResponse
from app.db.models.chat_model import Chat

from app.erp_tools.router.supply_chain_router import supply_chain_router
from app.erp_tools.modules.supply_chain import tools

import re

LOCATION_ALIAS = {
    "hn": "hà nội",
    "ha noi": "hà nội",
    "hà nội": "hà nội",

    "hcm": "hồ chí minh",
    "tphcm": "hồ chí minh",
    "sài gòn": "hồ chí minh",
    "sg": "hồ chí minh",
}

# =============================
# CONFIG LLM
# =============================
genai.configure(api_key=settings.GOOGLE_API_KEY)
llm = genai.GenerativeModel("gemini-2.5-flash")

def build_supply_chain_prompt(question: str, erp_json: dict | list) -> str:
    return f"""
Bạn là trợ lý ERP doanh nghiệp, chuyên mảng Supply Chain.

⚠️ QUY TẮC BẮT BUỘC:
- DỮ LIỆU ERP là SỰ THẬT TUYỆT ĐỐI
- KHÔNG suy luận
- KHÔNG gộp trạng thái
- KHÔNG diễn giải ngoài dữ liệu

⚠️ QUY ƯỚC NGHIỆP VỤ (CỰC KỲ QUAN TRỌNG):
- Chỉ được nói "sắp hết hàng" nếu sản phẩm nằm trong danh sách "low_stock"
- "dead_stock" = lâu không xuất, KHÔNG PHẢI sắp hết
- Nếu quantity > 0 và không nằm trong "low_stock" → KHÔNG được nói sắp hết
- Nếu không có dữ liệu → nói rõ "chưa có dữ liệu"

CÂU HỎI:
{question}

DỮ LIỆU ERP (JSON):
{erp_json}

YÊU CẦU:
- 1–3 câu
- Tiếng Việt chuẩn nghiệp vụ ERP
"""

def _extract_code(text: str) -> str | None:
    """
    Tách mã nghiệp vụ dạng PO-001, GR-002, PR-003, GI-004
    """
    match = re.search(r"\b[A-Z]{2,3}-\d+\b", text.upper())
    return match.group(0) if match else None

def _extract_warehouse_name(text: str) -> str | None:
    match = re.search(r"kho\s+([a-zA-ZÀ-ỹ\s]+)", text.lower())
    if match:
        return match.group(1).strip().title()
    return None

def _extract_product_keyword(text: str) -> str | None:
    """
    Ưu tiên keyword người dùng nói:
    - iPhone 15
    - Dell XPS
    - SKU
    """
    match = re.search(
        r"(iphone\s*\d+|dell\s*xps\s*\d*|[A-Z0-9\-]{4,})",
        text,
        re.IGNORECASE
    )
    return match.group(1) if match else None


def _extract_warehouse_name(text: str) -> str | None:
    text_lower = text.lower()

    # Ưu tiên alias
    for alias, normalized in LOCATION_ALIAS.items():
        if alias in text_lower:
            return normalized.title()

    # Fallback: lấy sau chữ "kho"
    match = re.search(r"kho\s+([a-zA-ZÀ-ỹ\s]+)", text_lower)
    if match:
        return match.group(1).strip().title()

    return None


def _extract_product_sku(text: str) -> str | None:
    """
    Tách SKU dạng:
    - IPHONE-15
    - DELL-XPS13
    """
    match = re.search(r"\b[A-Z0-9\-]{4,}\b", text.upper())
    return match.group(0) if match else None

import re

def _extract_product_id(text: str) -> int | None:
    """
    Tách product_id từ câu hỏi.
    Ví dụ:
    - 'Sản phẩm 1 còn hàng không?'
    - 'Cho tôi xem tồn kho sản phẩm 12'
    """
    match = re.search(r"sản phẩm\s+(\d+)", text.lower())
    return int(match.group(1)) if match else None


def _handle_procurement_intent(intent: str, query: str):
    if intent == "get_purchase_order_status":
        po_code = _extract_code(query)
        if not po_code:
            return {"error": "Không xác định được mã PO"}
        return tools.get_purchase_order_status(po_code)

    if intent == "get_po_receiving_progress":
        po_code = _extract_code(query)
        return tools.get_po_receiving_progress(po_code)

    raise NotImplementedError(f"Procurement intent chưa hỗ trợ: {intent}")

def _handle_inventory_intent(intent: str, query: str):
    # 1. Ưu tiên alias / keyword
    keyword = normalize_product_keyword(query)
    if keyword:
        return tools.get_inventory_stock_by_keyword(keyword)

    # 2. Fallback theo product_id (RẤT QUAN TRỌNG)
    product_id = _extract_product_id(query)
    if product_id:
        return tools.get_inventory_stock(product_id)

    return {"error": "Không xác định được sản phẩm"}



def save_history(db: Session, sid: str, q: str, a: str):
    db.add(Chat(
        session_id=sid,
        question=q,
        answer=a
    ))
    db.commit()

def chat_supply_chain_internal(query: str) -> Dict[str, Any]:
    route = supply_chain_router(query)

    if route["domain"] == "unknown":
        return None

    domain = route["domain"]
    intent = route["intent"]

    # Ví dụ procurement multi-tool
    if domain == "procurement" and intent == "get_po_receiving_progress":
        po_id = 1  # demo
        return {
            "receiving_progress": tools.get_po_receiving_progress(po_id),
            "missing_items": tools.get_received_vs_ordered_quantity(po_id)
        }
    
    if intent == "get_stock_by_warehouse":
        warehouse = _extract_warehouse_name(query)
        product = normalize_product_keyword(query)

        if warehouse and product:
            return tools.get_stock_by_warehouse_and_product(
                warehouse, product
            )

        return tools.get_stock_by_warehouse(warehouse)

    if intent == "get_purchase_order_status":
        po_code = _extract_code(query)
        return {
            "purchase_order": tools.get_purchase_order_status(po_code)
        }
    
    if intent == "get_inventory_transaction_logs":
        product_id = _extract_product_id(query)
        return {
            "inventory_logs": tools.get_inventory_transaction_logs(product_id)
        }

    # Inventory demo
    if domain == "inventory" and intent == "get_inventory_stock":
        product_id = 1
        return {
            "inventory": tools.get_inventory_stock(product_id),
            "alerts": tools.get_stock_alerts()
        }

    return {"message": "Intent chưa hỗ trợ"}

def handle_chat_supply_chain(request: ChatRequest) -> ChatResponse:
    chat_db = SessionLocal()

    try:
        # 1️⃣ TOOL + ROUTER
        erp_result = chat_supply_chain_internal(
            request.question
        )

        if erp_result is None:
            return ChatResponse(
                answer="❌ Câu hỏi không thuộc nghiệp vụ Supply Chain.",
                response_type="OUT_OF_SCOPE",
                sources=[]
            )

        # 2️⃣ BUILD PROMPT
        prompt = build_supply_chain_prompt(
            request.question,
            erp_result
        )

        # 3️⃣ LLM DIỄN ĐẠT
        answer = llm.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1
            )
        ).text

        # 4️⃣ SAVE HISTORY
        save_history(
            chat_db,
            request.session_id,
            request.question,
            answer
        )

        return ChatResponse(
            answer=answer,
            response_type="ERP_SUPPLY_CHAIN",
            sources=[]
        )

    finally:
        chat_db.close()

