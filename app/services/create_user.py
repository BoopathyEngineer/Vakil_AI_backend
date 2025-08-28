from fastapi import  HTTPException
from app.crud.user_crud import get_user_details,get_role_name
from app.models.user_models import User
from app.models.email_models import EmailId
from app.utils.auth_utils import get_hashed_password
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def create_users(user,data,session):
    logger.info(f"Request received to create user with email: {getattr(user, 'email', None)} [status_code=100]")
    try:  
        detail = ''
        if get_user_details(session, {'phone_no': user.phone_number}):
            detail += 'mobile'
        if get_user_details(session, {'email': user.email}):
            if detail == '':
                detail += 'email'
            else:
                detail += ' & email'
        if detail != '':
            logger.warning(f"Duplicate user data: {detail} already exists for email: {user.email} [status_code=400]")
            raise HTTPException(status_code=400, detail=detail + ' already exists')  
           
        # hash_password = get_hashed_password(user.password)
        role_id = get_role_name(session,{'roles':user.role})
        new_user = User(
            username=user.username,
            dob=user.dob,
            phone_no=user.phone_number,
            email=user.email,
            role=role_id.id,
            university=user.university,
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        new_email_instance = EmailId(email_id = user.email)
        session.add(new_email_instance)
        session.commit()
        
        logger.info(f"User created successfully with email: {user.email} [status_code=200]")
        return {"message": "User created successfully"}
    
    except Exception as e:
        logger.error(f"Error creating user with email: {getattr(user, 'email', None)} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
