from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)        
    content = Column(String, nullable=False)         
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) 
    )