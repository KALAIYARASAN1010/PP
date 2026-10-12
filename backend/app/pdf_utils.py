import os
import io
from typing import Tuple
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from fastapi import HTTPException, UploadFile

def extract_text_from_pdf(file_bytes: bytes, filename: str = "document.pdf") -> str:
    """
    Extracts text from a PDF byte stream using pypdf.
    Validates file integrity and rejects empty or corrupted files.
    """
    if not file_bytes or len(file_bytes.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file '{filename}' is empty (0 bytes). Please upload a valid document."
        )

    # Validate PDF signature magic bytes
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail=f"File '{filename}' does not have a valid PDF header (%PDF-). File may be corrupted or not a PDF."
        )

    try:
        stream = io.BytesIO(file_bytes)
        reader = PdfReader(stream)
        
        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"PDF '{filename}' contains zero pages."
            )

        extracted_text_chunks = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text_chunks.append(page_text.strip())

        full_text = "\n\n".join(extracted_text_chunks).strip()
        if not full_text:
            return "[PDF uploaded: scanned/empty text layer detected]"

        return full_text

    except PdfReadError as pe:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse PDF '{filename}': Corrupted file structure ({str(pe)})."
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=400,
            detail=f"Error reading PDF '{filename}': {str(e)}"
        )
