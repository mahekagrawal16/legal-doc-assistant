# main.py — FastAPI Backend Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.routes.upload import router as upload_router
from app.routes.ask import router as ask_router

app = FastAPI(
    title="Legal Document Assistant API",
    description="RAG-based legal document Q&A backend",
    version="2.0.0"
)

# Allow Streamlit frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(ask_router, prefix="/ask", tags=["Ask"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Legal Assistant API is running"}