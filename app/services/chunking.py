# app/services/chunking.py — Intelligent Text Chunking
#
# WHY CHUNKING MATTERS:
#   LLMs have context limits. Sending an entire 50-page contract as context is expensive
#   and inaccurate. By splitting into meaningful clauses/sections, we retrieve only the
#   relevant pieces for each question — this is the "R" in RAG.
#
# STRATEGY USED (Hybrid):
#   1. Try heading-based splitting first (sections like "PAYMENT TERMS", "TERMINATION")
#   2. Fall back to sentence-window chunking with overlap for documents without clear headings
#   3. Each chunk stays between 150–1500 characters for optimal embedding quality
#
# ALTERNATIVES:
#   - RecursiveCharacterTextSplitter (LangChain): generic, reliable
#   - SpaCy sentence splitter: linguistically aware
#   - NLTK tokenizer: lightweight sentence segmentation

import re
from langchain_core.documents import Document

MIN_CHUNK_LEN = 100
MAX_CHUNK_LEN = 1500
OVERLAP_SENTENCES = 2  # Sentences to overlap between chunks for context continuity


def chunk_text_smart(text: str, source: str) -> list[Document]:
    """
    Tries heading-based chunking first.
    Falls back to sentence-window chunking if no headings found.
    """
    chunks = _heading_based_chunks(text, source)

    if len(chunks) < 2:
        # Likely no clear headings — use sentence windowing
        chunks = _sentence_window_chunks(text, source)

    return chunks


def _heading_based_chunks(text: str, source: str) -> list[Document]:
    """
    Splits text on ALL-CAPS headings (common in legal contracts).
    E.g., "PAYMENT TERMS", "1. CONFIDENTIALITY", "CLAUSE 4 – TERMINATION"
    """
    # Match lines that are mostly uppercase and at least 4 chars
    pattern = r"\n\s*([A-Z][A-Z\s\d\.\–\-:]{3,})\s*\n"
    matches = list(re.finditer(pattern, text))
    chunks = []

    if not matches:
        return chunks

    for i, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        if len(content) >= MIN_CHUNK_LEN:
            # Further split very long sections
            if len(content) > MAX_CHUNK_LEN:
                sub_chunks = _split_long_section(content, source, section_title)
                chunks.extend(sub_chunks)
            else:
                chunks.append(Document(
                    page_content=content,
                    metadata={"source": source, "section": section_title}
                ))

    return chunks


def _sentence_window_chunks(text: str, source: str, window: int = 8) -> list[Document]:
    """
    Splits text into rolling sentence windows with overlap.
    Good for narrative-style documents without explicit headings.
    """
    # Simple sentence splitter (handles abbreviations better than split('.'))
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    chunks = []
    step = max(1, window - OVERLAP_SENTENCES)

    for i in range(0, len(sentences), step):
        window_sents = sentences[i: i + window]
        content = " ".join(window_sents).strip()

        if len(content) >= MIN_CHUNK_LEN:
            chunks.append(Document(
                page_content=content,
                metadata={
                    "source": source,
                    "section": f"Passage {i // step + 1}",
                }
            ))

    return chunks


def _split_long_section(text: str, source: str, section: str) -> list[Document]:
    """Breaks oversized sections into smaller overlapping chunks."""
    words = text.split()
    chunks = []
    chunk_size = 200  # words per chunk
    overlap = 30

    for i in range(0, len(words), chunk_size - overlap):
        content = " ".join(words[i: i + chunk_size])
        if len(content) >= MIN_CHUNK_LEN:
            chunks.append(Document(
                page_content=content,
                metadata={"source": source, "section": f"{section} (part {i // (chunk_size - overlap) + 1})"}
            ))

    return chunks