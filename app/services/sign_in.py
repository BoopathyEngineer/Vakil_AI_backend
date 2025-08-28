from fastapi.exceptions import HTTPException
from app.models.user_models import User
from app.crud.user_crud import fetch_user_details,get_role_name
from app.schemas.auth_schemas import Token
from app.utils.auth_utils import create_access_token, verify_password
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def user_signin(email,password,session):
    logger.info(f"Request received to sign in user with email: {email} [status_code=100]")
    try:
        user_email = fetch_user_details(session,email)

        if user_email:
            if verify_password(password,user_email.password):
                university = user_email.university if user_email.university else ''
                roles = get_role_name(session,{'id':user_email.role})
                jwt_token = create_access_token({'id': user_email.id, 'name': user_email.username, 'role': user_email.role, 'university': university})
                Token.is_verified = True
                Token.jwt_token = jwt_token
                Token.email = user_email.email
                Token.role_id = user_email.role
                Token.role = roles.roles
                Token.user_id = user_email.id
                Token.university = university
                logger.info(f"User signed in successfully: {email} [status_code=200]")
                return Token
            else:
                Token.is_verified = False
                Token.jwt_token = ''
                Token.email = ''
                Token.role_id = None
                Token.role = ''
                Token.user_id = None
                Token.university = ''
                logger.warning(f"Incorrect password for user: {email} [status_code=400]")
                return Token
            
        else:
            logger.warning(f"User not found for email: {email} [status_code=404]")
            raise HTTPException(status_code=500, detail=f"Incorrect email or password")

    except Exception as e:
        logger.error(f"Error during sign in for email: {email} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

