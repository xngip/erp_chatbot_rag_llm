# app/services/chat_rag.py
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.db.schemas.chat_schema import ChatRequest, ChatResponse, RAGSource, ChatMessage
from app.db.models.chat_model import Chat
from app.rag.retriever import query_vectorstore

# =============================
# CONFIG LLM
# =============================
genai.configure(api_key=settings.GOOGLE_API_KEY)
llm = genai.GenerativeModel("gemini-2.5-flash-lite")

# =============================
def load_history(db: Session, sid: str, limit=5):
    rows = (
        db.query(Chat)
        .filter(Chat.session_id == sid)
        .order_by(Chat.timestamp.desc())
        .limit(limit)
        .all()
    )
    rows.reverse()
    return "\n".join([f"{r.question}\n{r.answer}" for r in rows])

# =============================
def handle_chat_rag(request: ChatRequest) -> ChatResponse:
    chat_db = SessionLocal()

    try:
        history = load_history(chat_db, request.session_id)

        result = query_vectorstore(request.question, n_results=3)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]

        context = "\n\n".join(docs)

        prompt = f"""
Bạn là trợ lý tư vấn ERP.

LỊCH SỬ:
{history}

TÀI LIỆU:
{context}

CÂU HỎI:
{request.question}

Trả lời bằng tiếng Việt.
"""

        answer = llm.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3
            )
        ).text

        chat_db.add(Chat(
            session_id=request.session_id,
            question=request.question,
            answer=answer
        ))
        chat_db.commit()

        sources = [
            RAGSource(
                doc_id=i,
                title=metas[i].get("source", "Không rõ"),
                content=docs[i],
                source=metas[i].get("source", "Không rõ"),
                score=None
            )
            for i in range(len(docs))
        ]

        return ChatResponse(
            answer=answer,
            response_type="RAG",
            sources=sources
        )

    finally:
        chat_db.close()
