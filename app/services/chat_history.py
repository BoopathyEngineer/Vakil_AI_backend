from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from app.models.chat import Chat
from app.schemas.chat_schema import ChatResponse, Message
from app.services.create_chat import validate_user
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def chat_history_service(user_id, session):
    logger.info(f"Request received to fetch chat history for user_id: {user_id} [status_code=100]")
    try:
        user = validate_user(user_id, session)
        if not user:
            logger.warning(f"User not found for user_id: {user_id} [status_code=404]")
            raise HTTPException(status_code=404, detail="User not found")

        chats = session.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.asc()).all()

        if not chats:
            logger.info(f"No chats found for user_id: {user_id} [status_code=204]")
            return JSONResponse(status_code=200, content=[])
        
        chat_responses = []
        for chat in chats:
            messages = []
            for m in chat.messages:
                # Handle both old and new message formats
                message_data = {
                    "message_id": m.get("message_id") or m.get("resposne_id"),
                    "query": m.get("query", ""),
                    "answer": m.get("answer", {}) if isinstance(m.get("answer"), dict) else {"response": m.get("answer", "")}
                }
                messages.append(Message(**message_data))

            chat_response = ChatResponse(
                user_id=chat.user_id,
                chat_id=chat.chat_id,
                messages=messages
            )
            chat_responses.append(chat_response)

        logger.info(f"Successfully fetched chat history for user_id: {user_id} [status_code=200]")
        return chat_responses
    except Exception as e:
        logger.error(f"Error fetching chat history for user_id: {user_id} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

