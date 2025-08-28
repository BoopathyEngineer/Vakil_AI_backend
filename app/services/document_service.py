import PyPDF2
from docx import Document
import os
import tempfile
from typing import Optional
from fastapi import UploadFile

async def extract_text_from_document(file: UploadFile) -> Optional[str]:
    """Extract text from uploaded PDF or DOCX files"""
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        text = ""
        
        if file.filename.endswith('.pdf'):
            with open(tmp_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text += page.extract_text()

        elif file.filename.endswith(('.docx', '.doc')):
            doc = Document(tmp_path)
            for para in doc.paragraphs:
                text += para.text + "\n"

        elif file.filename.endswith('.txt'):
            with open(tmp_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()

        # Clean up temporary file
        os.unlink(tmp_path)

        return text.strip()
    except Exception as e:
        print(f"Error extracting text from document: {str(e)}")
        return None

async def answer_from_document(query: str, document_text: str) -> str:
    """Generate an answer based on the document content"""
    prompt = f"""You are analyzing a legal document with the following content:

{document_text}

Please answer the following question based on the document content only:
{query}

If the answer cannot be found in the document, say "I cannot find the answer to this question in the provided document."
Format your response in HTML with proper paragraphs using <p> tags.
"""
    # Using the existing LLM utility
    from app.utils.llm_utils import generate_response
    
    response = await generate_response(prompt)
    processed_response = response.replace("```html", "").replace('```json', "").replace("```", "")
    return {"answer": processed_response}
