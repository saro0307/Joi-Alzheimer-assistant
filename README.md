# 🧠 Joi — LangChain RAG Memory Bot

A deployable memory chatbot using **LangChain RAG**, **FAISS vector search**, and **Groq's free LLM API**. Anyone can use it via a URL — no installs needed on their end.

## Architecture

```
index.html  (frontend — served by Flask)
    │  fetch()
    ▼
Joi.py  (Flask REST API)
    │
    ├── POST /memories  →  save fact to memories.json
    │                      + Groq LLM confirmation
    │
    └── POST /ask       →  LangChain RAG:
                           1. Embed all memories → FAISS vector store
                           2. Retrieve top-k relevant memories
                           3. Llama 3.1 (via Groq) answers using retrieved context
```

## Files

| File | Role |
|---|---|
| `Joi.py` | Backend — LangChain RAG + Flask API + serves frontend |
| `index.html` | Frontend — chat UI |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render.com one-click deployment config |
| `memories.json` | Auto-created, persists memories across sessions |
| `.env` | Your API keys (never commit this to GitHub) |

---

## 💻 Run Locally

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Get a free Groq API key
1. Sign up free at https://console.groq.com
2. Go to **API Keys** → **Create API Key**
3. Copy the key (looks like `gsk_...`)

### Step 3 — Create a `.env` file in the project folder
```
GROQ_API_KEY=gsk_your_key_here
```

### Step 4 — Run
```bash
python Joi.py
```

### Step 5 — Open in browser
Go to **http://localhost:5000** — that's it!

---

## 🚀 Deploy to Render (public URL for everyone)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Joi memory bot"
git remote add origin https://github.com/YOUR_USERNAME/joi-memory-bot.git
git push -u origin main
```

> ⚠️ Make sure `.env` is in `.gitignore` so your API key is never pushed!

### Step 2 — Deploy on Render
1. Go to https://render.com → sign up free
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Render auto-reads `render.yaml`
5. Add environment variable:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_key_here`
6. Click **Deploy** → wait ~3 mins

### Step 3 — Share your URL
Once deployed, share `https://your-app-name.onrender.com` — anyone can use it with no setup!

---

## API Reference

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `/` | — | Serves the frontend (index.html) |
| GET | `/health` | — | Health check |
| GET | `/memories` | — | List all memories |
| POST | `/memories` | `{"text":"..."}` | Save fact + get AI confirmation |
| POST | `/ask` | `{"question":"..."}` | RAG answer from memories |
| DELETE | `/memories/<id>` | — | Delete one memory |
| DELETE | `/memories` | — | Clear all memories |

---

## How RAG works here

1. User asks a question
2. All stored memories are embedded using `all-MiniLM-L6-v2` (runs on server)
3. FAISS finds the most semantically relevant memories
4. Top memories are passed as context to **Llama 3.1** via Groq API
5. Llama answers based only on retrieved memories — no hallucination

---

## Notes

- **Free tier on Render** spins down after 15 mins of inactivity — first visit after a gap takes ~30 sec to wake up
- All users currently share the same `memories.json` — add a database for per-user memories
- The deprecation warning from `langchain_huggingface` on startup is harmless — it comes from inside that library, not your code
