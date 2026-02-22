from sqlalchemy.orm import Session
from models.message import Message

def save_message(db: Session, username: str, content: str) -> Message:
    message = Message(username=username, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_recent_messages(db: Session, limit: int = 50) -> list[Message]:
    return (
        db.query(Message)
        .order_by(Message.timestamp.asc())  # Urut dari yang terlama
        .limit(limit)
        .all()
    )