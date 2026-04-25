# app/routes/upload.py — File Upload & Processing Pipeline
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os

from app.utils.file_utils import save_uploaded_file
from app.services.extractor import extract_text_from_file
from app.services.chunking import chunk_text_smart
from app.services.embeddings import generate_and_store_embeddings

router = APIRouter()
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts PDF or DOCX files, extracts text, chunks intelligently,
    embeds with HuggingFace + FAISS, and stores the vector index.

    FIX: We now do `await file.read()` BEFORE passing bytes to the
    sync save utility. This prevents the SpooledTemporaryFile cursor
    issue that was causing the browser to receive the raw file bytes
    (triggering an unwanted download) instead of saving server-side.
    """
    all_chunks = []
    processed_files = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".pdf", ".docx"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Only PDF and DOCX are accepted."
            )

        # ✅ KEY FIX: await the read() here in the async context
        content = await file.read()

        filename = save_uploaded_file(file.filename, content, UPLOAD_DIR)
        file_path = os.path.join(UPLOAD_DIR, filename)

        try:
            text = extract_text_from_file(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from '{filename}': {str(e)}"
            )

        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Document '{filename}' appears to be empty or unreadable."
            )

        chunks = chunk_text_smart(text, file.filename)   # Use original name in metadata
        all_chunks.extend(chunks)
        processed_files.append({"filename": file.filename, "chunks": len(chunks)})

    if not all_chunks:
        raise HTTPException(status_code=400, detail="No text chunks could be generated.")

    generate_and_store_embeddings(all_chunks)

    return {
        "status": "success",
        "message": f"Processed {len(processed_files)} file(s) into {len(all_chunks)} chunks.",
        "files": processed_files,
        "total_chunks": len(all_chunks),
    }