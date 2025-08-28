from fastapi.exceptions import HTTPException
from app.models.chat import Chat
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def delete_chat_history(chat_id, session):
    logger.info(f"Request received to delete chat history for chat_id: {chat_id} [status_code=100]")
    try:
        chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
        if chat is None:
            logger.warning(f"Chat not found for chat_id: {chat_id} [status_code=404]")
            raise HTTPException(status_code=404, detail="Chat not found")
        
        session.delete(chat)
        session.commit()
        logger.info(f"Chat history deleted successfully for chat_id: {chat_id} [status_code=200]")
        return {"message": "Chat history deleted successfully"}
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting chat history for chat_id: {chat_id} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")