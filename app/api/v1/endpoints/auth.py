from fastapi import Depends, Body
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.logger.logger import logger_setup
from app.schemas.auth_schemas import AuthResponseDetails,Token
from app.schemas.user_schemas import CreateUserPassword
from app.services.forgot_password import reset_password
from app.services.get_email_for_verify import get_email_for_verify
from app.services.verify_email import verify_email
from app.services.user_signing_up import user_signing_up
from app.services.sign_in import user_signin

logger = logger_setup(__name__)
auth_router = APIRouter(tags=['auth'])

# Mail Verification Endpoint
@auth_router.post("/get_email/{email}",response_model=AuthResponseDetails)
async def get_email(email: str, new_user: bool, session: Session = Depends(get_db)):
    logger.info("Action: Verify Email | Status: 200 | Message: Request received")
    return get_email_for_verify(email, new_user, session)

@auth_router.post("/verify_email/{email}/{otp}",response_model=AuthResponseDetails)
async def verify(email: str, otp: int, session: Session = Depends(get_db)):
    logger.info("Action: Verify OTP | Status: 200 | Message: Request received")
    return verify_email(email, otp,session)

# Signup Endpoint
@auth_router.post("/signup", response_model=AuthResponseDetails)
async def sign_up(user: CreateUserPassword, session: Session = Depends(get_db)):
    print("Hello2")
    try:
        result = user_signing_up(user, session)
        logger.info(f"Signup successful for email: {user.email}")
        return result
    except Exception as e:
        logger.error(f"Signup failed for email: {user.email}. Error: {str(e)}")
        raise

# Login Endpoint
@auth_router.post("/check_info",response_model=Token)
async def login_check(email: str = Body(...), password: str = Body(...), session: Session = Depends(get_db)):
    logger.info("Action: Login | Status: 200 | Message: Request received")
    return user_signin(email,password,session)

# Forgot Password Endpoint
@auth_router.put("/forgot_password", response_model=AuthResponseDetails)
async def forgot_password(email: str = Body(...), password: str = Body(...), session: Session = Depends(get_db)):
    logger.info("Action: Forgot Password | Status: 200 | Message: Request received")
    return reset_password(email,password,session)