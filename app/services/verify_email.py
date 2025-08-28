import time
from fastapi import HTTPException
from app.crud.user_crud import get_user_by_email
from app.models.email_models import EmailId
from app.schemas.auth_schemas import AuthResponseDetails
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def verify_email(email,otp,session):
    logger.info(f"Request received to verify email: {email} [status_code=100]")
    try: 
        user_email = get_user_by_email(session,email)

        if user_email is None:
            logger.warning(f"Email not found in database: {email} [status_code=404]")
            raise HTTPException(status_code=404, detail="Email not found in database.")
        elif user_email.otp == otp and round(time.time()) - user_email.otp_time <= 360: 
            AuthResponseDetails.message = "Email Verified Successfully"
            logger.info(f"Email verified successfully: {email} [status_code=200]")
            return AuthResponseDetails
        else:
            logger.warning(f"OTP does not match for email: {email} [status_code=400]")
            raise HTTPException(status_code=404, detail="OTP does not match.")
        
    except Exception as e:
        logger.error(f"Error verifying email: {email} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

