# 🧠 Joi — LangChain RAG Memory Bot

A deployable memory chatbot using **LangChain RAG**, **FAISS vector search**, and **HuggingFace Inference API**. Anyone can use it via a URL — no installs needed.

## Architecture

```
index.html  (frontend)
    │  fetch()
    ▼
memory_bot.py  (Flask REST API)
    │
    ├── POST /memories  →  save fact to memories.json
    │                      + LLM confirmation via HuggingFace
    │
    └── POST /ask       →  LangChain RAG:
                           1. Embed all memories → FAISS vector store
                           2. Retrieve top-k relevant memories
                           3. Mistral-7B answers using retrieved context
```

## Files

| File | Role |
|---|---|
| `memory_bot.py` | Backend — LangChain RAG + Flask API |
| `index.html` | Frontend — chat UI, talks to backend |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render.com deployment config (one-click) |
| `memories.json` | Auto-created, persists memories |

---

## 🚀 Deploy to Render (public URL for everyone)

### Step 1 — Get a free HuggingFace token
1. Sign up free at https://huggingface.co
2. Go to https://huggingface.co/settings/tokens
3. Create a token with **Read** role → copy it

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "Joi memory bot"
git remote add origin https://github.com/YOUR_USERNAME/joi-memory-bot.git
git push -u origin main
```

### Step 3 — Deploy on Render
1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo
3. Render auto-detects `render.yaml`
4. Add environment variable:
   - Key: `HF_TOKEN`
   - Value: `hf_your_token_here`
5. Click **Deploy** → wait ~3 mins

### Step 4 — Update the frontend
Open `index.html` and change line:
```js
const BACKEND_URL = "http://localhost:5000";
```
to:
```js
const BACKEND_URL = "https://your-app-name.onrender.com";
```
Then host `index.html` anywhere (GitHub Pages, Vercel, Netlify — all free).

---

## 💻 Run Locally

```bash
# Install
pip install -r requirements.txt

# Set your HF token
export HF_TOKEN="hf_..."     # Linux/Mac
set HF_TOKEN=hf_...          # Windows

# Run backend
python memory_bot.py

# Open frontend
# Just open index.html in your browser (make sure BACKEND_URL = "http://localhost:5000")
```

---

## API Reference

| Method | Endpoint | Body | Description |
|---|---|---|---|
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
4. Top memories are passed as context to `Mistral-7B-Instruct` via HuggingFace Inference API
5. Mistral answers based only on retrieved memories