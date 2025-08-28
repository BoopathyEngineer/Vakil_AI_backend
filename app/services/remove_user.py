from fastapi import  HTTPException
from app.models.user_models import User
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def remove_user(user_id,data,session):
    logger.info(f"Request received to remove user with user_id: {user_id} [status_code=100]")
    try:  
        user = session.query(User).filter(User.id == user_id).delete()
        session.commit()
        logger.info(f"User deleted successfully with user_id: {user_id} [status_code=200]")
        return {"message": "User deleted successfully"}
            
    except Exception as e:
        logger.error(f"Error deleting user with user_id: {user_id} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

