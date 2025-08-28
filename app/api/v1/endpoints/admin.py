from fastapi import Depends,File,UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.logger.logger import logger_setup
from app.schemas.auth_schemas import AuthResponseDetails
from app.schemas.user_schemas import Base64PDFRequest
from app.schemas.user_schemas import CreateUser, UserHistory, UpdateUser
from app.services.create_user import create_users
from app.services.create_bulk_user import create_bulk_user
from app.services.update_user import update_user
from app.services.list_users_details import list_users_details
from app.services.remove_user import remove_user
from app.services.invoice_pdf import process_invoice
from app.utils.auth_utils import JWTBearer
logger = logger_setup(__name__)

admin_router = APIRouter(tags=['admin'])

@admin_router.post("/create_user", response_model=AuthResponseDetails)
async def create(user: CreateUser, data:object=Depends(JWTBearer()), session: Session = Depends(get_db)):
    logger.info("Action: Create User | Status: 200 | Message: Request received")
    return create_users(user,data,session)

@admin_router.post("/bulk_user_create", response_model=AuthResponseDetails)
async def create_user(file: UploadFile = File(...), data:object=Depends(JWTBearer()), session: Session = Depends(get_db)):
    logger.info("Action: Create Bulk User | Status: 200 | Message: Request received")
    return await create_bulk_user(file,data,session)

@admin_router.put("/update_users", response_model=AuthResponseDetails)
async def update(user_id: int, user: UpdateUser, data:object=Depends(JWTBearer()), session: Session = Depends(get_db)):
    logger.info("Action: Update User | Status: 200 | Message: Request received")
    return update_user(user_id,user,data,session)

@admin_router.get("/list_users_details", response_model=list[UserHistory])
async def list_users(data:object=Depends(JWTBearer()), session: Session = Depends(get_db)):
    logger.info("Action: List User | Status: 200 | Message: Request received")
    return list_users_details(data,session)

@admin_router.delete("/remove_user", response_model=AuthResponseDetails)
async def delete(user_id: int, data:object=Depends(JWTBearer()), session: Session = Depends(get_db)):
    logger.info("Action: Delete User | Status: 200 | Message: Request received")
    return remove_user(user_id,data,session)

@admin_router.post("/upload-invoice")
async def upload_invoice(file: Base64PDFRequest):
    return await process_invoice(file)