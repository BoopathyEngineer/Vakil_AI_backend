from fastapi import  HTTPException
from app.crud.user_crud import get_user_details,get_user_info
from app.models.user_models import User
from app.utils.auth_utils import get_hashed_password
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def update_user(user_id,user,data,session):
    logger.info(f"Request received to update user with user_id: {user_id} [status_code=100]")
    try:
        detail = ''
        if get_user_info(session, user_id, {'phone_no': user.phone_number}):
            detail += 'mobile'
        if get_user_info(session, user_id, {'email': user.email}):
            if detail == '':
                detail += 'email'
            else:
                detail += ' & email'
        if detail != '':
            logger.warning(f"Duplicate user data for user_id: {user_id}: {detail} already exists [status_code=400]")
            raise HTTPException(status_code=400, detail=detail + ' already exists')  
           
        existing_user = session.query(User).filter(User.id == user_id).first()
        
        if not existing_user:
            logger.warning(f"User not found for user_id: {user_id} [status_code=404]")
            raise HTTPException(status_code=404, detail=f"An error occurred")          

        # Update user details
        existing_user.username = user.username
        existing_user.dob = user.dob
        existing_user.email = user.email
        existing_user.phone_no = user.phone_number
        existing_user.university = user.university

        # Commit changes to the database
        session.commit()
        session.close()

        logger.info(f"User updated successfully for user_id: {user_id} [status_code=200]")
        return {"status": "success", "message": "User updated successfully"}

    except Exception as e:
        logger.error(f"Error updating user with user_id: {user_id} [status_code=400] - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")          