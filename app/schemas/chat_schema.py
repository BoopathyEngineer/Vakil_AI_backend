from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    question: str
    user_id: int
    chat_id: str

class Message(BaseModel):
    message_id: str
    query: str
    answer: dict 
    created_at: datetime = Field(default_factory=lambda:datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class ChatResponse(BaseModel):
    user_id: int
    chat_id: Optional[str | None] = None
    messages: List[Message] 
    
class Link(BaseModel):
    Title: str
    URL: str

class WebpageData(BaseModel):
    Links: List[Link]
    Images: List[str]
    Videos: List[Link]

class ImageResponse(BaseModel):
    user_id: int
    query: str
    image_urls: List[dict]

class ResourceResponse(BaseModel): 
    user_id: int
    query: str
    video_urls: List[Link]
    links: List[Link]

class CreateChatRequest(BaseModel):
    user_id: int

class CreateChatResponse(BaseModel):
    user_id: int
    chat_id: str

class ChatRequestSchema(BaseModel):
    question: str
    user_id: int
    chat_id: str
    document_text: str | None = None


    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question should not be empty")
        return value
