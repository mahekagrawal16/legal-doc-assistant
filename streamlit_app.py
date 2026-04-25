# streamlit_app.py — LexSimple Legal Document Assistant

import streamlit as st
import requests
import os
import re as _re

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="LexSimple – Legal Document Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
  --pink:#E040A0;--pink-l:#FCE4F5;--pink-d:#A0005A;
  --blue:#3B82F6;--blue-l:#EFF6FF;--blue-d:#1D4ED8;
  --yellow:#F59E0B;--yel-l:#FFFBEB;--yel-d:#B45309;
  --purple:#7C3AED;--dark:#1A1030;--mid:#4B3F72;
  --grad:linear-gradient(135deg,#FCE4F5 0%,#EFF6FF 45%,#FFFBEB 100%);
  --grad-vivid:linear-gradient(135deg,#E040A0 0%,#3B82F6 50%,#F59E0B 100%);
}
html,body,[data-testid="stAppViewContainer"]{background:var(--grad)!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1A0A2E 0%,#2D1B4E 60%,#0F2154 100%)!important;border-right:1px solid rgba(224,64,160,0.3);}
[data-testid="stSidebar"] *{color:#E8D5FF!important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#fff!important;}
.hero{background:var(--grad-vivid);border-radius:24px;padding:3rem 2.5rem 2.5rem;margin-bottom:2rem;position:relative;overflow:hidden;box-shadow:0 20px 60px rgba(224,64,160,0.25),0 4px 20px rgba(59,130,246,0.2);}
.hero::before{content:'';position:absolute;top:-40px;right:-40px;width:220px;height:220px;background:rgba(255,255,255,0.08);border-radius:50%;}
.hero::after{content:'';position:absolute;bottom:-60px;left:30%;width:300px;height:300px;background:rgba(255,255,255,0.06);border-radius:50%;}
.hero-title{font-family:'Playfair Display',serif!important;font-size:3rem;font-weight:700;color:white;line-height:1.1;margin:0 0 0.5rem;text-shadow:0 2px 20px rgba(0,0,0,0.2);}
.hero-sub{font-size:1.1rem;color:rgba(255,255,255,0.88);font-weight:300;margin:0;}
.hero-badge{display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);border-radius:100px;padding:4px 16px;font-size:0.8rem;color:white;font-weight:500;letter-spacing:1px;text-transform:uppercase;margin-bottom:1rem;}
.card{background:white;border-radius:20px;padding:2rem;border:1px solid rgba(124,58,237,0.1);box-shadow:0 4px 24px rgba(59,130,246,0.08);margin-bottom:1.5rem;}
.card-title{font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--dark);margin:0 0 1rem;display:flex;align-items:center;gap:10px;}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--blue-l);border:1px solid rgba(59,130,246,0.3);border-radius:100px;padding:4px 14px;font-size:0.78rem;color:var(--blue-d);font-weight:500;margin:4px 4px 4px 0;}
.step{display:flex;align-items:flex-start;gap:1rem;margin-bottom:1.2rem;}
.step-num{width:36px;height:36px;border-radius:50%;background:var(--grad-vivid);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;flex-shrink:0;}
.step-text{font-size:0.92rem;color:var(--mid);line-height:1.5;padding-top:6px;}
.step-text strong{color:var(--dark);}
.footer{text-align:center;padding:2rem 0 1rem;font-size:0.8rem;color:rgba(75,63,114,0.6);}
.footer strong{color:var(--purple);}
hr{border:none;border-top:1px solid rgba(124,58,237,0.12);margin:1.5rem 0;}
.stButton>button{background:var(--grad-vivid)!important;color:white!important;border:none!important;border-radius:12px!important;padding:0.65rem 2rem!important;font-weight:600!important;font-size:1rem!important;font-family:'DM Sans',sans-serif!important;box-shadow:0 4px 20px rgba(224,64,160,0.4)!important;transition:all 0.25s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(224,64,160,0.5)!important;}
.stTextArea>div>div>textarea{border:1.5px solid rgba(124,58,237,0.25)!important;border-radius:12px!important;background:white!important;font-family:'DM Sans',sans-serif!important;font-size:1rem!important;padding:0.7rem 1rem!important;color:var(--dark)!important;}
.stTextArea>div>div>textarea:focus{border-color:var(--pink)!important;box-shadow:0 0 0 3px rgba(224,64,160,0.15)!important;}
[data-testid="stFileUploader"]{border:2px dashed rgba(124,58,237,0.3)!important;border-radius:16px!important;background:linear-gradient(135deg,rgba(252,228,245,0.4),rgba(239,246,255,0.4))!important;}
.stSuccess{background:linear-gradient(135deg,#F0FDF4,#DCFCE7)!important;border:1px solid #86EFAC!important;border-radius:12px!important;}
.stError{background:linear-gradient(135deg,#FFF1F2,#FFE4E6)!important;border:1px solid #FCA5A5!important;border-radius:12px!important;}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def check_backend():
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=3).status_code == 200
    except Exception:
        return False


def render_answer(text: str) -> str:
    """Convert LLM answer text → clean HTML. Handles bullets and **bold**."""
    # If the text still looks like raw JSON, extract just the answer field
    if text.strip().startswith('{'):
        try:
            import json
            obj = json.loads(text)
            text = obj.get("answer", text)
        except Exception:
            # Try to extract answer field with regex
            m = _re.search(r'"answer"\s*:\s*"(.*?)"(?:,|\s*})', text, _re.DOTALL)
            if m:
                text = m.group(1).replace('\\n', '\n').replace('\\"', '"')

    text = text.replace("\\n", "\n").replace("\\r\\n", "\n").replace("\\r", "\n")
    text = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith(("• ", "- ", "* ")):
            content = s[2:].strip()
            out.append(
                f"<div style='display:flex;gap:10px;align-items:flex-start;margin:.35rem 0;line-height:1.6;'>"
                f"<span style='color:#E040A0;font-weight:900;flex-shrink:0;margin-top:2px;'>•</span>"
                f"<span>{content}</span></div>"
            )
        else:
            out.append(f"<p style='margin:.4rem 0;line-height:1.65;'>{s}</p>")
    return "".join(out)


# ── Session state ─────────────────────────────────────────────────────────────
for key, val in {
    "doc_uploaded": False,
    "chat_history": [],
    "q_staging": "",        # sample button writes here before widget renders
    "ask_triggered": False, # flag: sample question was just submitted
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 0.5rem;'>
      <div style='font-family:Playfair Display,serif;font-size:1.6rem;font-weight:700;
                  background:linear-gradient(90deg,#E040A0,#3B82F6,#F59E0B);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        ⚖️ LexSimple
      </div>
      <div style='font-size:0.78rem;color:rgba(232,213,255,0.6);letter-spacing:1.5px;
                  text-transform:uppercase;margin-top:2px;'>Legal AI Assistant</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    backend_ok = check_backend()
    if backend_ok:
        st.markdown("🟢 **Backend:** Connected")
    else:
        st.markdown("🔴 **Backend:** Offline")
        st.markdown("""<div style='background:rgba(245,158,11,0.15);border-radius:10px;
            padding:0.8rem;font-size:0.82rem;color:#FCD34D;margin-top:0.5rem;'>
            Start:<br><code style='color:#F59E0B;'>uvicorn main:app --reload</code>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### How it works")
    for i, (title, desc) in enumerate([
        ("Upload","PDF or DOCX legal document"),
        ("Extract","Text pulled from document"),
        ("Chunk","Split into legal clauses"),
        ("Embed","Vectorised with MiniLM"),
        ("Retrieve","Top clauses for your query"),
        ("Answer","LLaMA 3 explains plainly"),
    ], 1):
        st.markdown(f"""<div class='step'>
          <div class='step-num'>{i}</div>
          <div class='step-text'><strong>{title}</strong><br>{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Tech Stack")
    for icon, name, role in [
        ("🔷","FastAPI","Backend API"),("🎈","Streamlit","Frontend UI"),
        ("📄","PyMuPDF + python-docx","Extraction"),("🤗","MiniLM-L6-v2","Embeddings"),
        ("🔎","FAISS","Vector Search"),("⚡","Groq / LLaMA 3","LLM"),
    ]:
        st.markdown(f"""<div style='display:flex;gap:8px;align-items:center;margin-bottom:8px;
            font-size:0.84rem;color:rgba(232,213,255,0.85);'>
          <span>{icon}</span>
          <div><strong style='color:white;'>{name}</strong><br>
          <span style='font-size:0.75rem;color:rgba(232,213,255,0.55);'>{role}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Document Index", use_container_width=True):
        try:
            import shutil
            if os.path.exists("vectorstore/legal_index"):
                shutil.rmtree("vectorstore/legal_index")
            st.session_state.doc_uploaded = False
            st.session_state.chat_history = []
            st.success("Index cleared!")
        except Exception as e:
            st.error(f"Could not clear: {e}")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <div class='hero-badge'>⚡ Powered by RAG + LLaMA 3</div>
  <div class='hero-title'>Legal Documents,<br>Made Simple.</div>
  <p class='hero-sub'>Upload any contract or agreement. Ask questions in plain language.<br>
  Get clear, jargon-free answers — instantly.</p>
</div>""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")


# ── LEFT: Upload ──────────────────────────────────────────────────────────────
with col_left:
    st.markdown("""<div class='card'>
      <div class='card-title'><span>📂</span> Upload Document</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("**Supported formats:** PDF · DOCX")
    uploaded_file = st.file_uploader(
        "Drop your legal document here",
        type=["pdf", "docx"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        kb = uploaded_file.size / 1024
        st.markdown(f"""<div style='background:var(--blue-l);border:1px solid rgba(59,130,246,0.2);
            border-radius:12px;padding:0.75rem 1rem;margin:0.75rem 0;
            font-size:0.88rem;color:var(--blue-d);display:flex;gap:10px;align-items:center;'>
          📎 <strong>{uploaded_file.name}</strong>
          <span style='color:rgba(29,78,216,0.6);'>· {kb:.1f} KB</span>
        </div>""", unsafe_allow_html=True)

        if st.button("⚡ Process Document", use_container_width=True):
            if not backend_ok:
                st.error("Backend is offline. Start: `uvicorn main:app --reload`")
            else:
                with st.spinner("Extracting · Chunking · Embedding…"):
                    try:
                        files = [("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))]
                        r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=120)
                        if r.status_code == 200:
                            data = r.json()
                            st.session_state.doc_uploaded = True
                            st.session_state.chat_history = []
                            st.success(f"✅ Ready! Created **{data['total_chunks']}** searchable chunks.")
                        else:
                            st.error(f"Upload failed: {r.json().get('detail', 'Unknown error')}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style='background:var(--yel-l);border:1px solid rgba(245,158,11,0.25);
        border-radius:14px;padding:1rem 1.2rem;'>
      <div style='font-weight:600;color:var(--yel-d);font-size:0.88rem;margin-bottom:0.5rem;'>
        💡 Works great with:</div>
      <div style='font-size:0.84rem;color:#92400E;line-height:1.8;'>
        • Rental / Lease Agreements<br>• Employment Contracts<br>
        • Service Level Agreements (SLA)<br>• Non-Disclosure Agreements (NDA)<br>
        • Business Partnership Agreements
      </div>
    </div>""", unsafe_allow_html=True)


# ── RIGHT: Q&A ────────────────────────────────────────────────────────────────
with col_right:
    st.markdown("""<div class='card'>
      <div class='card-title'><span>💬</span> Ask the Document</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.doc_uploaded:
        st.markdown("""<div style='text-align:center;padding:3rem 1rem;'>
          <div style='font-size:3rem;'>📄</div>
          <div style='color:rgba(75,63,114,0.5);margin-top:0.5rem;font-size:0.95rem;'>
            Upload a document first to unlock Q&A</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("**Quick questions to try:**")
        SAMPLE_QS = [
            "What are the payment terms and due dates?",
            "Can I terminate this agreement early? What are the conditions?",
            "What happens if there is a breach of contract?",
            "What are my obligations as a party to this agreement?",
            "Are there any confidentiality or non-disclosure clauses?",
        ]

        # Sample buttons: write question into staging, set trigger flag, rerun
        for sq in SAMPLE_QS:
            if st.button(f"↗ {sq}", key=f"sq_{sq[:25]}", use_container_width=True):
                st.session_state.q_staging = sq
                st.session_state.ask_triggered = True
                # No explicit rerun — Streamlit reruns automatically on button click

        st.markdown("---")

        # Text area: value= from staging (empty string = cleared)
        # No key= so Streamlit doesn't lock it; value= always respected
        question = st.text_area(
            "Or type your own question:",
            value=st.session_state.q_staging,
            height=100,
            placeholder="e.g. What happens if I miss a payment?",
        )

        ask_col, clear_col = st.columns([3, 1])
        with ask_col:
            ask_btn = st.button("🔍 Get Answer", use_container_width=True)
        with clear_col:
            if st.button("Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.q_staging = ""
                st.session_state.ask_triggered = False
                st.rerun()

        # Determine what to send: triggered by sample button OR manual ask
        should_ask = ask_btn and question.strip()
        if st.session_state.ask_triggered:
            should_ask = True
            question = st.session_state.q_staging

        if should_ask and question.strip():
            # Reset flags immediately
            st.session_state.q_staging = ""
            st.session_state.ask_triggered = False

            with st.spinner("Finding relevant clauses and generating answer…"):
                try:
                    r = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": question.strip()},
                        timeout=60,
                    )
                    if r.status_code == 200:
                        data = r.json()
                        answer_val = data.get("answer", "")
                        # Guard: if answer is still a dict, extract text
                        if isinstance(answer_val, dict):
                            answer_val = answer_val.get("answer", str(answer_val))
                        st.session_state.chat_history.append({
                            "question": question.strip(),
                            "answer": answer_val,
                            "confidence": data.get("confidence", "MEDIUM"),
                            "exact_quotes": data.get("exact_quotes", []),
                            "uncertainty_flags": data.get("uncertainty_flags", []),
                            "sources": data.get("sources", []),
                        })
                        st.rerun()
                    else:
                        st.error(f"❌ {r.json().get('detail', 'Error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend is offline.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Chat history ──────────────────────────────────────────────────────
        if st.session_state.chat_history:
            st.markdown("---")
            for item in reversed(st.session_state.chat_history):

                # Question bubble
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,var(--pink-l),var(--blue-l));
                    border-radius:16px 16px 4px 16px;padding:0.9rem 1.2rem;
                    margin-bottom:0.5rem;font-size:0.95rem;
                    border:1px solid rgba(224,64,160,0.15);'>
                  <span style='font-size:0.72rem;color:var(--pink-d);font-weight:700;
                      text-transform:uppercase;letter-spacing:1px;'>Your Question</span><br>
                  <strong>{item['question']}</strong>
                </div>""", unsafe_allow_html=True)

                # Confidence badge
                conf = item.get("confidence", "MEDIUM")
                conf_map = {
                    "HIGH":   ("🟢", "#D1FAE5", "#065F46", "#6EE7B7"),
                    "MEDIUM": ("🟡", "#FEF3C7", "#92400E", "#FCD34D"),
                    "LOW":    ("🔴", "#FEE2E2", "#991B1B", "#FCA5A5"),
                }
                icon, bg, fg, border = conf_map.get(conf, ("⚪","#F3F4F6","#374151","#D1D5DB"))
                st.markdown(f"""
                <div style='margin:.3rem 0 .6rem;'>
                  <span style='background:{bg};color:{fg};border:1px solid {border};
                      border-radius:100px;padding:4px 14px;font-size:.72rem;
                      font-weight:800;letter-spacing:.6px;'>
                    {icon}&nbsp; {conf} CONFIDENCE
                  </span>
                </div>""", unsafe_allow_html=True)

                # Strip gap-acknowledgment sentences from answer body
                # e.g. "There are no specific due dates mentioned" → move to flags
                import re as _re2
                raw_answer = item["answer"]
                gap_patterns = [
                    r'[^.]*?(?:no specific|not mentioned|not specified|not addressed|'
                    r'does not (?:mention|address|include|state|cover)|'
                    r'no (?:clause|provision|section|reference)|'
                    r'is not (?:explicitly|directly|clearly) (?:stated|mentioned|addressed))'
                    r'[^.]*\.',
                ]
                extracted_gaps = []
                cleaned_answer = raw_answer
                for pat in gap_patterns:
                    matches = _re2.findall(pat, cleaned_answer, flags=_re2.IGNORECASE)
                    for m in matches:
                        m = m.strip()
                        if m and m not in extracted_gaps:
                            extracted_gaps.append(m)
                    cleaned_answer = _re2.sub(pat, '', cleaned_answer, flags=_re2.IGNORECASE)
                cleaned_answer = _re2.sub(r'\n{3,}', '\n\n', cleaned_answer).strip()

                # Merge extracted gaps into uncertainty flags (deduped)
                existing_flags = item.get("uncertainty_flags", [])
                all_flags = list(existing_flags)
                for gap in extracted_gaps:
                    if not any(gap.lower()[:30] in f.lower() for f in all_flags):
                        all_flags.append(gap)

                answer_html = render_answer(cleaned_answer if cleaned_answer else raw_answer)
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#F0FDF4,#EFF6FF);
                    border:1.5px solid #86EFAC;border-radius:16px;
                    padding:1.2rem 1.5rem;margin:.3rem 0 .7rem;
                    font-size:.95rem;color:#1A1030;'>
                  <div style='font-size:.68rem;color:#16A34A;font-weight:800;
                      text-transform:uppercase;letter-spacing:1px;margin-bottom:.55rem;'>
                    ✦ Answer
                  </div>
                  {answer_html}
                </div>""", unsafe_allow_html=True)

                # Exact quotes — only if present and not trivially short
                quotes = [q for q in item.get("exact_quotes", []) if len(q.strip()) > 15]
                if quotes:
                    q_html = "".join(
                        f"<div style='background:#FFFBEB;border-left:3px solid #F59E0B;"
                        f"border-radius:0 8px 8px 0;padding:.55rem .9rem;margin:.3rem 0;"
                        f"font-size:.82rem;font-style:italic;color:#78350F;line-height:1.55;'>"
                        f"&#8220;{q}&#8221;</div>"
                        for q in quotes
                    )
                    st.markdown(f"""
                    <div style='font-size:.68rem;font-weight:800;color:#92400E;
                        text-transform:uppercase;letter-spacing:.8px;margin:.4rem 0 .2rem;'>
                      📜 From the document:
                    </div>{q_html}""", unsafe_allow_html=True)

                # Uncertainty flags — only show genuinely important ones
                # all_flags = stored flags + any gaps extracted from answer body above
                flags = [
                    f for f in all_flags
                    if f.strip() and any(kw in f.lower() for kw in [
                        "not address", "not cover", "not include", "not found",
                        "silent", "ambiguous", "may depend", "unclear",
                        "not explicitly state", "no clause", "not specified",
                        "does not state", "does not mention"
                    ])
                ]
                if flags:
                    f_html = "".join(
                        f"<div style='display:flex;gap:7px;align-items:flex-start;"
                        f"font-size:.82rem;color:#C2410C;margin:.2rem 0;line-height:1.5;'>"
                        f"<span style='flex-shrink:0;'>⚠️</span><span>{f}</span></div>"
                        for f in flags
                    )
                    st.markdown(f"""
                    <div style='background:#FFF7ED;border:1px solid #FED7AA;
                        border-radius:10px;padding:.6rem .9rem;margin:.4rem 0;'>
                      <div style='font-size:.68rem;font-weight:800;color:#C2410C;
                          text-transform:uppercase;letter-spacing:.8px;margin-bottom:.3rem;'>
                        ⚠️ Important note:
                      </div>{f_html}
                    </div>""", unsafe_allow_html=True)

                # Sources
                if item.get("sources"):
                    chips = "".join(f"<span class='chip'>📎 {s}</span>" for s in item["sources"])
                    st.markdown(f"<div style='margin:.3rem 0 1.4rem;'>{chips}</div>",
                                unsafe_allow_html=True)

                st.markdown("<hr>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
  Built with <strong>FastAPI</strong> · <strong>LangChain</strong> · <strong>FAISS</strong>
  · <strong>Groq LLaMA 3</strong> · <strong>Streamlit</strong><br>
  For learning purposes only. Not a substitute for professional legal advice.
</div>""", unsafe_allow_html=True)