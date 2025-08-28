from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.services.document_service import extract_text_from_document
from app.services.image_service import process_image
from app.core.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/extract")
async def extract_document_text(
    file: UploadFile,
    session: Session = Depends(get_db)
):
    """Extract text from an uploaded document or image"""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Check if it's an image file
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    is_image = any(file.filename.lower().endswith(ext) for ext in image_extensions)

    if is_image:
        result = await process_image(file)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to process image")
        return result
    else:
        # Handle documents (PDF, DOCX, TXT)
        text = await extract_text_from_document(file)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from document")
        return {"text": text}
