import os
import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are LexSimple, a legal document assistant. Your job is to read the provided document sections and answer questions clearly and completely.

RULES:
1. Use ONLY information from the document context. Never add outside knowledge.
2. Give a COMPLETE answer — extract ALL relevant details from the document, not just one sentence.
3. Use exact numbers, dates, names, timeframes, and amounts from the document.
4. If the document does not address the question at all, say exactly: "This agreement does not include any clause about [topic]."
5. Never guess. Never say "it is likely" or "typically".
6. For casual questions like "explain like I'm 10" or "explain me" — use very simple words a child understands. Short sentences. Real-life comparisons. No legal terms.
7. For specific questions like "what are payment terms" — be thorough and list every relevant detail found in the document.

WHEN DOCUMENT IS SILENT:
- If a topic is genuinely not in the document, say so directly and briefly.
- Do not repeat "not mentioned" multiple times — say it once and stop.

CONFIDENCE:
- HIGH: document has a direct clause answering this exactly
- MEDIUM: partial answer, some details missing
- LOW: document does not address this at all

OUTPUT FORMAT: Return ONLY a raw JSON object. No markdown. No ```json. Start with { end with }.

{
  "answer": "Complete answer here. Use \\n• for bullet points when listing multiple items.",
  "confidence": "HIGH",
  "confidence_reason": "One short sentence why.",
  "exact_quotes": ["verbatim text from document supporting the answer — only include if genuinely relevant"],
  "uncertainty_flags": ["Only add if document is completely silent on an important aspect"],
  "section_referenced": "e.g. Section 4 or Multiple sections or Not found"
}"""

HUMAN_TEMPLATE = """DOCUMENT SECTIONS:
{context}

QUESTION: {question}

Read all the document sections carefully. Extract every relevant detail that answers the question. Return only the JSON object."""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Get a free key at https://console.groq.com")
    return ChatGroq(
        api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.0,
        max_tokens=1500,
    )


def _build_context(docs: list) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        section = doc.metadata.get("section", f"Passage {i}")
        parts.append(f"[Section {i}: {section}]\n{doc.page_content.strip()}")
    return "\n\n".join(parts)


def _fix_unescaped_newlines(s: str) -> str:
    result = []
    in_string = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and in_string:
            result.append(c)
            i += 1
            if i < len(s):
                result.append(s[i])
        elif c == '"':
            in_string = not in_string
            result.append(c)
        elif in_string and c in ('\n', '\r'):
            result.append('\\n')
        else:
            result.append(c)
        i += 1
    return ''.join(result)


def _parse(raw: str) -> dict:
    cleaned = raw.strip()

    # Strip markdown fences
    if '```' in cleaned:
        for part in cleaned.split('```'):
            part = part.strip().lstrip('json').strip()
            if part.startswith('{'):
                cleaned = part
                break

    # Extract JSON object only
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    # Fix smart quotes
    cleaned = (cleaned
        .replace('\u201c', '"').replace('\u201d', '"')
        .replace('\u2018', "'").replace('\u2019', "'")
        .replace('\u2032', "'")
    )

    # Fix trailing commas
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

    # Fix bare newlines inside strings
    cleaned = _fix_unescaped_newlines(cleaned)

    try:
        result = json.loads(cleaned)
        result.setdefault("answer", cleaned)
        result.setdefault("confidence", "MEDIUM")
        result.setdefault("confidence_reason", "")
        result.setdefault("exact_quotes", [])
        result.setdefault("uncertainty_flags", [])
        result.setdefault("section_referenced", "")
        return result
    except json.JSONDecodeError:
        # If JSON parse fails, try to extract just the answer field via regex
        m = re.search(r'"answer"\s*:\s*"(.*?)"(?=\s*,|\s*})', cleaned, re.DOTALL)
        answer_text = m.group(1).replace('\\n', '\n') if m else raw.strip()
        return {
            "answer": answer_text,
            "confidence": "MEDIUM",
            "confidence_reason": "",
            "exact_quotes": [],
            "uncertainty_flags": [],
            "section_referenced": "",
        }


def explain_with_llm(question: str, docs: list) -> dict:
    context = _build_context(docs)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=HUMAN_TEMPLATE.format(context=context, question=question))
    ]
    response = get_llm().invoke(messages)
    return _parse(response.content)