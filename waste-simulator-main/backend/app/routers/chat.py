from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.schemas.chat import ChatIn, ChatOut
from app.services.chatbot_service import query_swms_assistant

router = APIRouter(prefix="/chat", tags=["AI Planning Assistant"])

@router.post("", response_model=ChatOut)
def chat_with_assistant(
    chat_in: ChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = query_swms_assistant(
        db=db,
        location_id=chat_in.location_id,
        question=chat_in.question
    )

    msg = ChatMessage(
        user_id=user.id,
        location_id=chat_in.location_id,
        question=chat_in.question,
        answer=result["answer"],
        evidence=result["evidence"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(msg)
    db.commit()

    return {
        "answer": result["answer"],
        "reply": result["answer"],
        "evidence": result["evidence"],
        "source_attribution": result["source_attribution"],
        "data_status": result["data_status"],
        "created_at": msg.created_at
    }
