import uuid
import datetime
from fastapi.exceptions import HTTPException
from app.models.chat import Chat
from app.schemas.chat_schema import ChatResponse, Message
from app.services.answer_gen_service import generate_answer_service
from app.services.create_chat import validate_user

async def chat_service(request, session):
    try:
        print("Processing chat request")
        # Validate required fields and user existence
        user = validate_user(int(request.user_id), session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not request.chat_id:
            raise HTTPException(status_code=400, detail="chat_id is required. Use /create-chat endpoint to create a new chat.")
        
        # Find the chat
        chat_id = request.chat_id
        chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        # Validate question (already validated by Pydantic model)
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        answer_response = await generate_answer_service(request.question)
        if not isinstance(answer_response, dict):
            raise HTTPException(
                status_code=500, detail="response must be a dictionary"
            )
        
        next_message_id = str(uuid.uuid4())

        new_message = dict(
            message_id=next_message_id,
            query=request.question,
            answer=answer_response,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )

        # Keep existing messages and append new one
        if not chat.messages:
            chat.messages = []
        chat.messages.append(new_message)
        session.add(chat)
        session.commit()

        messages = [Message(**m) for m in chat.messages]
        session.close()
        return ChatResponse(user_id=request.user_id, chat_id=chat_id, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

