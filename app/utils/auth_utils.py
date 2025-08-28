from datetime import datetime, timedelta
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException,Request
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

# Create a password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=180)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, "4Ag2XIsgdyPWPk3Q8xHGHS7DPWCzUNnOlGTHsYs252E", algorithm="HS256")

def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=300)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, "4Ag2XIsgdyPWPk3Q8xHGHS7DPWCzUNnOlGTHsYs252E", algorithm="HS256")

class JWTBearer(HTTPBearer):
    def __init__(self,auto_error:bool=True):
        super(JWTBearer,self).__init__(auto_error=auto_error)

    async def __call__(self, request:Request):
        credentials:HTTPAuthorizationCredentials=await super(JWTBearer,self).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403,detail="Invalid authentication scheme")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403,detail="Invalid token or expired token")
            return self.verify_jwt(credentials.credentials)
        else:
            raise HTTPException(status_code=403,detail="invalid authroization code")

    def verify_jwt(self,jwtoken:str)-> bool:
        isTokenValid: bool = False

        try:
            payload = jwt.decode(jwtoken,"4Ag2XIsgdyPWPk3Q8xHGHS7DPWCzUNnOlGTHsYs252E","HS256")
            return payload
        except: 
            payload=None