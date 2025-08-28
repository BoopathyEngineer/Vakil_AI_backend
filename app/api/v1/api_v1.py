from fastapi.routing import APIRouter
from fastapi import Depends
from app.api.v1.endpoints.auth import auth_router  
from app.api.v1.endpoints.chat_api import chat_router
from app.api.v1.endpoints.admin import admin_router
from app.api.v1.endpoints.document import document_router

api_v1 = APIRouter()

# Include all routers with their prefixes
api_v1.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

api_v1.include_router(
    chat_router,
    prefix="/chat",
    tags=["chat"]
)

api_v1.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"]
)

api_v1.include_router(
    document_router,
    prefix="/document",
    tags=["document"]
)
