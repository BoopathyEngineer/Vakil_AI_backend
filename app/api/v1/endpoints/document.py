from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.services.document_service import extract_text_from_document
from app.core.db import get_db
from sqlalchemy.orm import Session

document_router = APIRouter()

@document_router.post("/extract")
async def extract_document_text(
    file: UploadFile,
    session: Session = Depends(get_db)
):
    """Extract text from an uploaded document"""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    text = await extract_text_from_document(file)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract text from document")
        
    return {"text": text}
