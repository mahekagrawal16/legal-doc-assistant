# app/services/retriever.py — FAISS Similarity Search
#
# HOW IT WORKS:
#   1. Converts the user's question into the same embedding space as the stored chunks
#   2. Performs cosine similarity search across all stored vectors
#   3. Returns the top-k most relevant chunks as LangChain Document objects
#
# WHY k=4 BY DEFAULT:
#   Too few chunks → missing context. Too many → LLM gets confused by noise.
#   4 chunks of ~300 words each = ~1200 words of context, well within LLM limits.
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_PATH = "vectorstore/legal_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_relevant_chunks(query: str, k: int = 4) -> list:
    """
    Retrieves top-k relevant chunks for the query.

    Source deduplication: if multiple chunks from different sources score
    equally, we pick the best-scoring chunk per source, then take top-k overall.
    This prevents one document flooding the context when multiple docs are indexed.
    """
    if not os.path.exists(VECTOR_PATH):
        raise RuntimeError(
            "No document has been uploaded yet. Please upload a PDF or DOCX first."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = FAISS.load_local(
        VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    # Fetch more candidates than needed so deduplication has room to work
    candidates = vectorstore.similarity_search_with_score(query, k=k * 3)

    # Keep only one chunk per source file — the one with the best (lowest) score
    best_per_source = {}
    for doc, score in candidates:
        src = doc.metadata.get("source", "unknown")
        if src not in best_per_source or score < best_per_source[src][1]:
            best_per_source[src] = (doc, score)

    # Sort by score ascending (lower = more similar), take top-k
    ranked = sorted(best_per_source.values(), key=lambda x: x[1])[:k]

    # Tighter threshold: only keep chunks with cosine distance < 0.9
    # (was 1.2 — too loose, letting in tangentially related chunks from other topics)
    filtered = [doc for doc, score in ranked if score < 0.9]

    # Fallback: if everything exceeds threshold, return just the single best match
    # rather than dumping all low-quality chunks into the LLM context
    return filtered if filtered else ([ranked[0][0]] if ranked else [])