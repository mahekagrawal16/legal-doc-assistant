# 🧠 Legal Document Assistant

This is a beginner-friendly RAG-based (Retrieval-Augmented Generation) legal document assistant. It uses **OCR** to extract text from uploaded **PDF** and **DOCX** legal documents, chunks the text into clauses, stores their embeddings, and allows users to ask questions based on the content.

---

## 🔧 Tech Stack

- 🏗️ **FastAPI** – Backend APIs
- 🖼 **Streamlit** – Frontend user interface
- 🔍 **PyMuPDF** and **python-docx** – OCR/Text extraction
- 📚 **Langchain** – Embedding and RAG
- 🧠 **Groq/OpenAI/Any LLM** – For answering legal questions
- 🧠 **FAISS** – For fast vector similarity search

---

## ✅ Features

- Upload scanned **PDF** or **DOCX** legal documents.
- OCR + Clause-based text chunking.
- Embeddings + Vector DB retrieval.
- Ask natural language questions.
- Get simplified explanations from an LLM.

---

## 📁 File Structure

```
legal_doc_assistant/
│
├── app/
│   ├── routes/
│   │   └── upload.py               # Upload and embedding route
│   ├── services/
│   │   ├── ocr.py                  # PDF/DOCX text extraction
│   │   ├── chunking.py             # Clause chunking logic
│   │   └── embeddings.py           # Embedding + vectorstore logic
│   ├── utils/
│   │   └── file_utils.py           # Save file to disk
│   └── vectorstore/
│       └── (FAISS index files)
│
├── main.py                         # FastAPI entry point
├── streamlit_app.py                # Streamlit frontend
├── requirements.txt
├── appui.py                       #to run everything by one folder 
└── README.md
```
---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure to set your Groq API key:

```bash
export GROQ_API_KEY=your_key_here     # macOS/Linux
set GROQ_API_KEY=your_key_here        # Windows (CMD)
$env:GROQ_API_KEY="your_key_here"     # Windows (PowerShell)
```

### 2. Run the Application

```bash
python appui.py
```

- FastAPI backend will run on `http://localhost:8000`
- Streamlit frontend will run on `http://localhost:8501`

---
## 📥 How to Use

1. Upload `.pdf` or `.docx` legal documents using the Streamlit UI.
2. Documents are sent to the FastAPI backend, where:
   - Text is extracted using OCR.
   - Text is chunked into clauses.
   - Embeddings are generated and stored using FAISS.
3. Ask a question about the document.
4. The assistant retrieves relevant clauses and generates a user-friendly answer.

---

## ⚙️ Notes

- You **must upload documents** before asking questions.
- The backend uses a vectorstore (FAISS) to retrieve relevant text for answers.
- You can easily switch between OpenAI, Groq, or local models in `embeddings.py` and `query.py`.

--- 

## 📄 Supported Formats

- ✅ PDF (`.pdf`)
- ✅ Word Document (`.docx`)

---

## 🧪 Sample Questions

- "Can I terminate the agreement early?"
- "What happens if the rent is delayed?"
- "Who pays for repairs?"

--- 

## 🙌 Credits

- FastAPI + Streamlit
- LangChain + Groq API
- PyMuPDF + python-docx