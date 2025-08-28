from pydantic import BaseModel
from typing import Optional

class AuthResponseDetails(BaseModel):
    message : str

class Token(BaseModel):
    is_verified : bool
    jwt_token : str
    email : str
    role_id : int
    role : str
    user_id : Optional[int] = None
    university : str