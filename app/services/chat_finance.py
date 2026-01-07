# app/services/chat_finance.py
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.db.schemas.chat_schema import ChatRequest, ChatResponse
from app.db.models.chat_model import Chat

from app.erp_tools.router.finance_router import finance_router

# =============================
# CONFIG LLM
# =============================
genai.configure(api_key=settings.GOOGLE_API_KEY)
llm = genai.GenerativeModel("gemini-2.5-flash-lite")

# =============================
# FINANCE CONTROL PROMPT
# =============================
def build_finance_prompt(question: str, erp_json: dict | list) -> str:
    return f"""
Bạn là trợ lý kế toán – tài chính cho hệ thống ERP doanh nghiệp.

⚠️ QUY TẮC BẮT BUỘC:
- DỮ LIỆU ERP bên dưới là CHÍNH XÁC TUYỆT ĐỐI
- KHÔNG được suy diễn
- KHÔNG thêm hoặc bớt thông tin
- KHÔNG làm tròn số
- KHÔNG dự đoán tương lai
- KHÔNG đưa ra lời khuyên tài chính
- CHỈ diễn đạt lại dữ liệu có sẵn

CÂU HỎI NGƯỜI DÙNG:
{question}

DỮ LIỆU FINANCE (JSON):
{erp_json}

YÊU CẦU TRẢ LỜI:
- Ngắn gọn, rõ ràng
- Trung lập, đúng thuật ngữ kế toán
- Nếu không có dữ liệu, nói rõ "Không có dữ liệu"
- Không quá 3 câu
"""

# =============================
# SAVE CHAT HISTORY
# =============================
def save_history(db: Session, sid: str, q: str, a: str):
    db.add(Chat(
        session_id=sid,
        question=q,
        answer=a
    ))
    db.commit()

# =============================
# MAIN HANDLER
# =============================
def handle_chat_finance(request: ChatRequest) -> ChatResponse:
    chat_db = SessionLocal()

    try:
        erp_result = finance_router(
            query=request.question
        )

        if erp_result is not None:
            prompt = build_finance_prompt(
                request.question,
                erp_result
            )

            answer = llm.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1
                )
            ).text

            save_history(
                chat_db,
                request.session_id,
                request.question,
                answer
            )

            return ChatResponse(
                answer=answer,
                response_type="ERP_FINANCE",
                sources=[]
            )

        # 3️⃣ OUT OF SCOPE
        return ChatResponse(
            answer="❌ Câu hỏi không thuộc nghiệp vụ Tài chính – Kế toán.",
            response_type="OUT_OF_SCOPE",
            sources=[]
        )

    finally:
        chat_db.close()
