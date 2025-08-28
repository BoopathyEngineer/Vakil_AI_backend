from fastapi import Depends, HTTPException
from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from app.schemas.chat_schema import ChatRequest, ChatResponse, ChatRequestSchema, CreateChatRequest, CreateChatResponse
from app.services.answer_gen_service import response_gen 
from app.services.create_chat import create_chat_service
from app.services.chat_service import chat_service
from app.services.chat_history import chat_history_service
from app.services.question_suggestion import question_suggestion
from app.core.db import get_db
from sqlalchemy.orm import Session
from app.utils.auth_utils import JWTBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.chat import Chat
from app.schemas.chat_schema import ResourceResponse, ImageResponse
from app.services.create_chat import validate_user
from app.services.answer_gen_service import fetch_resources_and_videos
from app.services.delete_chat import delete_chat_history
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

chat_router = APIRouter(tags=["chat"])

@chat_router.post("/create-chat", response_model=CreateChatResponse)
async def create_chat(request: CreateChatRequest, session: Session = Depends(get_db)):
    logger.info("Action: Create new chat id | Status: 200 | Message: Request received")
    return create_chat_service(request, session)
    
@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: Session = Depends(get_db)):
    return await chat_service(request, session)

@chat_router.get("/chat/history", response_model=List[ChatResponse])
async def get_user_chat_history(user_id: int, session: Session = Depends(get_db)):
    logger.info("Action: List chat history | Status: 200 | Message: Request received")
    return chat_history_service(user_id, session)

@chat_router.post("/suggest_questions", response_model=List[str])
async def suggest_questions(request: ChatRequest, session: Session = Depends(get_db)):
    return await question_suggestion(request, session)

@chat_router.get('/chat/{chat_id}')
async def get_chat_route(chat_id: str, session: AsyncSession = Depends(get_db)):
    logger.info("Action: List chat details | Status: 200 | Message: Request received")
    chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    response = JSONResponse(content = {
        "chat_id": chat_id,
        "user_id": chat.user_id,
        "messages": chat.messages
    })
    return response

@chat_router.delete('/delete_chat_history/{chat_id}')
async def delete_chat(chat_id: str, session: Session = Depends(get_db)): 
    logger.info("Action: Delete Chat API | Status: 200 | Message: Request received")
    return delete_chat_history(chat_id, session) 

@chat_router.post("/response")
async def stream_response(
    request: Request,
    data: ChatRequestSchema,
    session: AsyncSession = Depends(get_db),
    user: object = Depends(JWTBearer())
):
    logger.info("Action: ChatBot API | Status: 200 | Message: Request received")
    response = StreamingResponse(response_gen(data,session), media_type="text/event-stream")
    return response

# @chat_router.get("/chat/history", response_model=List[ChatResponse])
# async def get_user_chat_history(user_id: int, session: Session = Depends(get_db)):
   
#     user = validate_user(user_id, session)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     chats = await get_user_chats(user_id)
#     if not chats:
#         return JSONResponse(status_code=200, content=[])
#     chat_responses = []
#     for chat in chats:
#         if not isinstance(chat, dict) or "messages" not in chat:
#             continue
#         messages = [Message(**m) for m in chat["messages"]]
#         chat_response = ChatResponse(
#             user_id=chat["user_id"],
#             chat_id=chat["chat_id"],
#             messages=messages
#         )
#         chat_responses.append(chat_response)

#     return chat_responses


# @chat_router.post("/fetch-resources-and-videos", response_model=ResourceResponse)
# async def get_resources_and_videos(
#         request: ChatRequest,
#         session: Session = Depends(get_db)
# ):
#     if not request.user_id:
#         raise HTTPException(status_code=400, detail="user_id is required")
    
#     if not request.prompt:
#         raise HTTPException(status_code=400, detail="Query is required for resource and video fetching")
    
#     if not request.chat_id:
#         raise HTTPException(status_code=400, detail="chat_id is required")
    
#     user = validate_user(int(request.user_id), session)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     resources_and_videos = fetch_resources_and_videos(request.prompt)

#     response = {
#         "user_id": request.user_id,
#         "query": request.prompt,
#         "video_urls": resources_and_videos["video_urls"],
#         "links": resources_and_videos["links"]
#     }
#     return response

# @chat_router.post("/fetch-images", response_model=ImageResponse)
# async def fetch_images_endpoint(
#     request: ChatRequest,
#     session: Session = Depends(get_db)
# ):
#     if not request.user_id:
#         raise HTTPException(status_code=400, detail="user_id is required")
    
#     if not request.prompt:
#         raise HTTPException(status_code=400, detail="Query is required for image fetching")
    
#     if not request.chat_id:
#         raise HTTPException(status_code=400, detail="chat_id is required")

#     user = validate_user(int(request.user_id), session)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     image_urls = fetch_images(request.prompt)
    
#     return ImageResponse(
#         user_id=request.user_id,
#         query=request.prompt,
#         image_urls=image_urls
#     )
