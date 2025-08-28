from pydantic import BaseModel 
from datetime import datetime
from app.schemas.hyperflx_enums import UserRoleSchema, UniversitySchema

class UserLogin(BaseModel):
    email: str
    password: str

class CreateUser(BaseModel):
    role: UserRoleSchema
    username: str
    dob: str
    phone_number: str 
    email: str
    university: str

class CreateUserPassword(CreateUser):
    password: str
    
class UpdateUser(BaseModel):
    username: str
    dob: str
    phone_number: str 
    email: str
    university: str

class UserHistory(BaseModel):
    id: int
    role: int
    username: str
    dob: str
    phone_number: str 
    email: str
    university: str

class Base64PDFRequest(BaseModel):
    file_base64: str