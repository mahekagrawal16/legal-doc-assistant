# app/services/embeddings.py — Vector Embeddings + FAISS Storage
#
# WHY EMBEDDINGS:
#   Text can't be directly compared mathematically. Embeddings convert text into
#   high-dimensional vectors where semantically similar text clusters together.
#   This lets us find relevant clauses by meaning, not just keyword matching.
#
# MODEL USED: sentence-transformers/all-MiniLM-L6-v2
#   - 384-dimensional vectors
#   - Extremely fast, runs on CPU
#   - Excellent quality for English legal text
#   - ~80MB download (cached after first use)
#
# ALTERNATIVES:
#   - BAAI/bge-small-en-v1.5: slightly better accuracy, same size
#   - intfloat/e5-small-v2: great for retrieval tasks
#   - text-embedding-3-small (OpenAI): cloud-based, better but costs money
#
# VECTOR DB: FAISS (Facebook AI Similarity Search)
#   - In-memory index saved to disk as .faiss + .pkl files
#   - Cosine similarity search in milliseconds even on large docs
#   - ALTERNATIVE: ChromaDB (persistent, easier to update), Pinecone (cloud)
import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_PATH = "vectorstore/legal_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def generate_and_store_embeddings(documents: list) -> None:
    # Always wipe the old index before building — never merge
    if os.path.exists(VECTOR_PATH):
        shutil.rmtree(VECTOR_PATH)
    os.makedirs(VECTOR_PATH, exist_ok=True)

    embeddings = _get_embeddings()
    vectorstore = FAISS.from_documents(documents, embedding=embeddings)
    vectorstore.save_local(VECTOR_PATH)


def clear_index() -> None:
    if os.path.exists(VECTOR_PATH):
        shutil.rmtree(VECTOR_PATH)