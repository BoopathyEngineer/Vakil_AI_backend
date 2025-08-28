from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.crud.user_crud import get_user_details
from fastapi import HTTPException
from app.schemas.chat_schema import CreateChatResponse
import uuid
from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def validate_user(user_id: int, db: Session):
    user = get_user_details(db, {"id": user_id})
    if not user:
        logger.warning(f"User not found for user_id: {user_id} [status_code=404]")
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_chat_service(request, session):
    logger.info(f"Request received to create chat for user_id: {getattr(request, 'user_id', None)} [status_code=100]")
    try:
        if not request.user_id:
            logger.warning("user_id is required for chat creation [status_code=400]")
            raise HTTPException(status_code=400, detail="user_id is required")

        user = validate_user(int(request.user_id), session)
        if not user:
            logger.warning(f"User not found for user_id: {request.user_id} [status_code=404]")
            raise HTTPException(status_code=404, detail="User not found")
        
        chat_id = str(uuid.uuid4())
        new_chat = Chat(
            chat_id=chat_id,
            user_id=request.user_id,
            messages=[]
        )
        session.add(new_chat)
        session.commit()    
        session.close()
        
        logger.info(f"Chat created successfully for user_id: {request.user_id}, chat_id: {chat_id} [status_code=200]")
        return CreateChatResponse(user_id=request.user_id, chat_id=chat_id)
    except Exception as e:
        logger.error(f"Error creating chat for user_id: {getattr(request, 'user_id', None)} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")