# app/services/chat_hrm.py
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.db.schemas.chat_schema import ChatRequest, ChatResponse
from app.db.models.chat_model import Chat

from app.erp_tools.router.hrm_router import hrm_router

# =============================
# CONFIG LLM
# =============================
genai.configure(api_key=settings.GOOGLE_API_KEY)
llm = genai.GenerativeModel("gemini-2.5-flash-lite")

# =============================
# HRM CONTROL PROMPT
# =============================
def build_hrm_prompt(question: str, erp_json: dict | list) -> str:
    return f"""
Bạn là trợ lý ERP doanh nghiệp.

⚠️ QUY TẮC BẮT BUỘC:
- DỮ LIỆU ERP bên dưới là SỰ THẬT TUYỆT ĐỐI
- KHÔNG được suy diễn
- KHÔNG thêm thông tin
- KHÔNG thay đổi ý nghĩa
- KHÔNG dự đoán tương lai
- CHỈ diễn đạt lại bằng tiếng Việt dễ hiểu

CÂU HỎI NGƯỜI DÙNG:
{question}

DỮ LIỆU ERP (JSON):
{erp_json}

YÊU CẦU TRẢ LỜI:
- 1–3 câu
- Ngắn gọn, rõ ràng
- Trung lập, không cảm xúc
""" 

# =============================
# SAVE HISTORY
# =============================
def save_history(db: Session, sid: str, q: str, a: str):
    db.add(Chat(session_id=sid, question=q, answer=a))
    db.commit()

# =============================
# MAIN HANDLER
# =============================
def handle_chat_hrm(request: ChatRequest) -> ChatResponse:
    chat_db = SessionLocal()

    try:
        erp_result = hrm_router(
            query=request.question,
            employee_id=1  # demo
        )

        if erp_result is not None:
            prompt = build_hrm_prompt(
                request.question,
                erp_result
            )
            answer = llm.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1
                )
            ).text

            save_history(chat_db, request.session_id, request.question, answer)

            return ChatResponse(
                answer=answer,
                response_type="ERP_HRM",
                sources=[]
            )

        return ChatResponse(
            answer="❌ Câu hỏi không thuộc nghiệp vụ HRM.",
            response_type="OUT_OF_SCOPE",
            sources=[]
        )

    finally:
        chat_db.close()
