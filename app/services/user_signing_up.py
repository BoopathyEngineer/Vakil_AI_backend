from datetime import datetime
from fastapi import  HTTPException
from app.crud.user_crud import get_user_by_email,get_user_details,get_role_name
from app.schemas.auth_schemas import AuthResponseDetails
from app.models.user_models import User
from datetime import datetime
from app.utils.auth_utils import get_hashed_password
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def user_signing_up(user,session):
    print("Hello1")
    logger.info(f"Request received to sign up user with email: {user.email} [status_code=100]")
    try:        
        print("Hello")   
        user_email = get_user_by_email(session,user.email)
        detail = ''
        if user_email:
            if get_user_details(session, {'phone_no': user.phone_number}):
                detail += 'mobile'
            if get_user_details(session, {'email': user.email}):
                if detail == '':
                    detail += 'email'
                else:
                    detail += ' & email'
            if detail != '':
                logger.warning(f"Duplicate user data for signup: {detail} already exists for email: {user.email} [status_code=400]")
                raise HTTPException(status_code=400, detail=detail + ' already exists')
        
            hash_password = get_hashed_password(user.password)
            role_id = get_role_name(session,{'roles':user.role})
            new_user_instance = User(
                    username = user.username,
                    dob = user.dob,
                    phone_no = user.phone_number,
                    email = user.email,
                    password = hash_password,
                    role = role_id.id,
                    university = user.university,
                )

            session.add(new_user_instance)
            session.commit()
            session.close()
            AuthResponseDetails.message = "Signup completed successfully"
            logger.info(f"User signed up successfully with email: {user.email} [status_code=200]")
            return AuthResponseDetails
        
        else:
            logger.warning(f"Email not verified for signup: {user.email} [status_code=404]")
            raise HTTPException(status_code=404, detail="Please verify your email ID before signing up")
    
    except Exception as e:
        logger.error(f"Error during signup for email: {user.email} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

