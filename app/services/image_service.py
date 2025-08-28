from PIL import Image
import pytesseract
import io
import base64
from fastapi import UploadFile
from typing import Optional

async def process_image(file: UploadFile) -> Optional[dict]:
    """Process uploaded image for analysis"""
    try:
        # Read the image file
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Extract text from image using OCR
        extracted_text = pytesseract.image_to_string(image)
        
        # Convert image to base64 for storing
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "text": extracted_text.strip(),
            "image_base64": img_str
        }
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
