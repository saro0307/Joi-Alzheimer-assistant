"""
Joi — LangChain RAG Memory Bot  (Backend)
==========================================
Stack:
  - Flask                        : REST API + serves index.html
  - LangChain                    : RAG chain, prompt templates, retriever
  - FAISS                        : in-process vector store (no extra server needed)
  - RecursiveCharacterTextSplitter : chunks large memories for better retrieval
  - HuggingFaceEmbeddings        : all-MiniLM-L6-v2 (runs on server, no key needed)
  - ChatGroq                     : Llama 3.1-8b-instant via Groq free API (fast)
  - python-dotenv                : loads GROQ_API_KEY from .env file

Deploy on Render:
  1. Push this repo to GitHub
  2. Create a new "Web Service" on render.com  →  connect the repo
  3. Add env var  GROQ_API_KEY = gsk_...   (your free key from console.groq.com)
  4. Render auto-detects render.yaml and deploys
  5. Share your Render URL — anyone can use the app
"""

import json, os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ── LangChain (modern v0.2+ imports — no pydantic v1/v2 conflicts) ────────
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ── Config ────────────────────────────────────────────────────────────────
MEMORY_FILE  = os.environ.get("MEMORY_FILE", "/data/memories.json" if os.path.isdir("/data") else "memories.json")
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BOT_NAME     = "Joi"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
EMBED_MODEL  = "BAAI/bge-small-en-v1.5"  # Tiny, no PyTorch, ~50MB RAM

app = Flask(__name__)
CORS(app)

# ── Embeddings — FastEmbed (no PyTorch, fits in 512MB RAM) ────────────────
print("⏳ Loading embedding model …")
embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL)
print("✅ Embeddings ready")

# ── LLM via Groq (free, fast) ─────────────────────────────────────────────
def get_llm():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com → API Keys"
        )
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=1024,
    )

# ── JSON storage ──────────────────────────────────────────────────────────
def load_memories() -> list[dict]:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memories(memories: list[dict]) -> None:
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f, indent=2)

# ── Text splitter — breaks large memories into retrievable chunks ──────────
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,      # each chunk max 300 characters
    chunk_overlap=50,    # overlap so context isn't lost at boundaries
    separators=["\n\n", "\n", ".", ",", " ", ""],
)

# ── Build FAISS vector store from all memories ────────────────────────────
def build_vectorstore(memories: list[dict]):
    """Split large memories into chunks, embed into FAISS for semantic search."""
    if not memories:
        return None

    docs = []
    for m in memories:
        chunks = text_splitter.split_text(m["text"])
        for i, chunk in enumerate(chunks):
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "id":        m["id"],
                    "timestamp": m["timestamp"],
                    "chunk":     i,
                    "source":    m["text"][:60],
                },
            ))

    return FAISS.from_documents(docs, embeddings)

# ── RAG prompt — single braces so LangChain recognises {context} & {input} 
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     f"You are {BOT_NAME}, a friendly personal memory assistant.\n"
     "Answer the question using ONLY the facts listed below.\n"
     "If the answer is not in the facts, say you don't have that information.\n"
     "Keep your answer concise and direct.\n\n"
     "Facts:\n{context}"),
    ("human", "{input}"),
])

def answer_with_rag(question: str, memories: list[dict]) -> str:
    if not memories:
        return "I don't have any memories stored yet. Tell me some facts first!"

    print(f"[DEBUG] Building vectorstore with {len(memories)} memories...")
    vectorstore        = build_vectorstore(memories)
    print("[DEBUG] Vectorstore built. Creating retriever...")
    retriever          = vectorstore.as_retriever(search_kwargs={"k": min(10, len(memories) * 3)})
    print("[DEBUG] Getting LLM...")
    llm                = get_llm()
    print("[DEBUG] Building RAG chain...")
    combine_docs_chain = create_stuff_documents_chain(llm, RAG_PROMPT)
    rag_chain          = create_retrieval_chain(retriever, combine_docs_chain)
    print("[DEBUG] Invoking RAG chain...")
    result             = rag_chain.invoke({"input": question})
    print("[DEBUG] Got result!")
    answer = result.get("answer", "I couldn't generate an answer.")
    lines  = [l.strip() for l in str(answer).splitlines() if l.strip()]
    return lines[-1] if lines else answer

# ── Confirmation ──────────────────────────────────────────────────────────
def confirm_memory(text: str) -> str:
    print(f"[DEBUG] Confirming memory: {text}")
    llm    = get_llm()
    print("[DEBUG] LLM ready, invoking...")
    prompt = (
        f"You are {BOT_NAME}, a friendly memory assistant. "
        f"Confirm storing this fact in ONE short warm sentence, "
        f"using the exact words from the fact:\n\n\"{text}\"\n\nConfirmation:"
    )
    reply = llm.invoke(prompt)
    print("[DEBUG] Got confirmation reply!")
    # Extract just the text content from the ChatMessage object
    text  = reply.content if hasattr(reply, "content") else str(reply)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else f"Got it, I've saved: \"{text}\""

# ── Question detection ─────────────────────────────────────────────────────
QUESTION_STARTS = (
    "who","what","where","when","why","how",
    "did","do","does","have","has","is","are",
    "was","were","can","could","would",
    "tell me","show me","list","find","which","give me",
)

def is_question(text: str) -> bool:
    t = text.strip().lower()
    if t.endswith("?"):
        return True
    return any(t.startswith(w) for w in QUESTION_STARTS)

# ── Serve frontend ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

# ── API routes ─────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME, "llm": "groq/llama-3.1-8b-instant"})


@app.route("/memories", methods=["GET"])
def get_memories():
    mems = load_memories()
    return jsonify({"memories": mems, "count": len(mems)})


@app.route("/memories", methods=["POST"])
def add_memory():
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify({"error": "No text provided"}), 400

    mems    = load_memories()
    next_id = max((m["id"] for m in mems), default=0) + 1
    entry   = {
        "id":        next_id,
        "text":      data["text"].strip(),
        "timestamp": datetime.now().isoformat(),
    }
    mems.append(entry)
    save_memories(mems)

    try:
        confirmation = confirm_memory(entry["text"])
    except Exception as e:
        confirmation = f"Saved! (AI confirmation unavailable: {e})"

    return jsonify({"memory": entry, "confirmation": confirmation}), 201


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    if not data or not data.get("question", "").strip():
        return jsonify({"error": "No question provided"}), 400

    mems = load_memories()
    try:
        answer = answer_with_rag(data["question"].strip(), mems)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"RAG error: {e}"}), 500

    return jsonify({"answer": answer})


@app.route("/memories/<int:memory_id>", methods=["DELETE"])
def delete_memory(memory_id):
    mems     = load_memories()
    filtered = [m for m in mems if m["id"] != memory_id]
    if len(filtered) == len(mems):
        return jsonify({"error": f"Memory #{memory_id} not found"}), 404
    save_memories(filtered)
    return jsonify({"message": f"Memory #{memory_id} deleted."})


@app.route("/memories", methods=["DELETE"])
def clear_memories():
    save_memories([])
    return jsonify({"message": "All memories cleared."})


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🧠  {BOT_NAME} is ready!")
    print(f"   Open this in your browser → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
