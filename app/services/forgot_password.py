from fastapi.exceptions import HTTPException
from app.models.user_models import User
from app.schemas.auth_schemas import AuthResponseDetails
from app.utils.auth_utils import get_hashed_password
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def reset_password(email,password,session):
    logger.info(f"Request received to reset password for email: {email} [status_code=100]")
    try:
        user_email = session.query(User).filter(User.email == email).first()
 
        if user_email:
          new_password = get_hashed_password(password)
          if new_password:
            user_email.password = new_password
            session.add(user_email)
            session.commit()
            session.close()
            AuthResponseDetails.message = "New password updated successfully!"
            logger.info(f"Password reset successful for email: {email} [status_code=200]")
          return AuthResponseDetails     
           
        else:
          logger.warning(f"Incorrect email or password for email: {email} [status_code=404]")
          raise HTTPException(status_code=500, detail=f"Incorrect email or password")
 
    except Exception as e:
      logger.error(f"Error resetting password for email: {email} [status_code=500] - {e}", exc_info=True)
      raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")