from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from app.services.retriever import get_relevant_chunks
from app.services.llm import explain_with_llm

router = APIRouter()


# ── Request  ─────────────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    k: int = Field(4, ge=1, le=10, description="Number of chunks to retrieve")


# ── Response  ─────────────────────────────────
class AnswerResponse(BaseModel):
    answer: str
    confidence: str                    
    confidence_reason: str
    exact_quotes: List[str]
    uncertainty_flags: List[str]
    section_referenced: str
    sources: List[str]


# ── Endpoint ─────────────────────────────────────────────────
@router.post("/", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Advanced Legal Q&A Endpoint:
    - Retrieves relevant clauses
    - Uses LLM for structured reasoning
    - Returns explainable + trustworthy response
    """

    # Validate input
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Retrieve relevant chunks
    try:
        chunks = get_relevant_chunks(request.question, k=request.k)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant clauses found. Try rephrasing your question."
        )

    #  Call LLM (expects structured JSON)
    try:
        result = explain_with_llm(request.question, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    #  Extract sources
    sources = list({doc.metadata.get("source", "Unknown") for doc in chunks})

    #  Safe fallback handling (VERY IMPORTANT)
    return AnswerResponse(
        answer=result.get("answer", "No answer generated."),
        confidence=result.get("confidence", "LOW"),
        confidence_reason=result.get("confidence_reason", "Not provided"),
        exact_quotes=result.get("exact_quotes", []),
        uncertainty_flags=result.get("uncertainty_flags", []),
        section_referenced=result.get("section_referenced", "Unknown"),
        sources=sources,
    )