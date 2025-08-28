from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    messages = Column(JSON, nullable=True)
    messages = Column(MutableList.as_mutable(JSON), nullable=True)
    created_at = Column(DateTime, default=datetime.now)  
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  
    