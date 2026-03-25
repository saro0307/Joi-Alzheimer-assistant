# 🧠 Joi - AI Memory Assistant for Alzheimer's Patients

---

## Problem Statement

Alzheimer's disease is one of the most devastating neurological conditions affecting millions of people worldwide. In its early stages, patients begin to lose their short-term memory forgetting names, places, daily events, and personal facts that define who they are.

Current solutions are largely passive like photo albums, written journals, caregiver notes none of which are intelligent, searchable, or interactive. Patients in early stages are still cognitively capable of recording their own memories, but they lack a tool that can store those memories and intelligently retrieve them when needed.

**Joi is built to solve this.** It gives early-stage Alzheimer's patients a simple, conversational interface to record and retrieve their own memories using AI, preserving their personal history before it's lost.

---

## Project Description

**Joi** is a beta-stage AI-powered memory assistant designed specifically for early-stage Alzheimer's patients. Patients can have a simple conversation with Joi — telling it facts about their life, their family, their preferences and Joi stores and remembers everything. When a patient forgets something, they can simply ask Joi and get an accurate, personalised answer drawn from their own recorded memories.

This is not a general-purpose chatbot. Joi answers **only from what the patient has told it** — no hallucinations, no invented information. Every answer is grounded in the patient's own words, retrieved using LangChain's RAG (Retrieval-Augmented Generation) pipeline.

This is a **beta version** — currently available via text input only. Future versions will integrate audio and video inputs, allowing patients to record memories hands-free using smart glasses such as **Meta Ray-Ban Smart Glasses** and **Google Glasses**, enabling live, real-time memory capture without any manual effort.

---

## 🏷️ Tags

`alzheimers` `memory-assistant` `langchain` `rag` `llm` `groq` `faiss` `flask` `python` `ai-health` `smart-glasses` `beta` `accessibility` `neurology` `early-stage-alzheimers` `conversational-ai`

---

## Architecture

```
Patient types a memory or question
            ↓
     index.html (frontend)
            ↓ fetch()
       Joi.py (Flask API)
            ↓
   ┌────────────────────────┐
   │     LangChain RAG      │
   │                        │
   │  RecursiveTextSplitter │  ← chunks large memories
   │         ↓              │
   │  FastEmbedEmbeddings   │  ← converts to vectors
   │         ↓              │
   │    FAISS Vectorstore   │  ← stores & retrieves
   │         ↓              │
   │  ChatGroq (Llama 3.1)  │  ← generates answer
   └────────────────────────┘
            ↓
    Answer returned to patient
```

---

## Current Features (Beta v1.0)

- 💬 **Text input** — patients type memories and questions
- 🧠 **Semantic memory retrieval** — finds relevant memories even with vague questions
- ✅ **Grounded answers** — Joi only answers from stored memories, never invents
- 🗂️ **Memory management** — view, delete, and clear memories
- 🌐 **Web-based** — accessible from any device with a browser
- ⚡ **Fast responses** — powered by Groq's free LLM API

---

## Roadmap

| Version | Feature |
|---|---|
| ✅ v1.0 (current) | Text input, RAG memory, web UI |
| 🔜 v2.0 | Audio input — patients speak their memories |
| 🔜 v3.0 | Smart glasses integration (Meta Ray-Ban, Google Glasses) |
| 🔜 v3.0 | Live video input — real-time memory capture |
| 🔜 v4.0 | Per-patient private memory with authentication |
| 🔜 v4.0 | Caregiver dashboard to monitor and manage memories |
| 🔜 v5.0 | Family sharing — loved ones can add memories too |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI Framework | LangChain (RAG pipeline) |
| Vector Store | FAISS |
| Embeddings | FastEmbed — `BAAI/bge-small-en-v1.5` |
| LLM | Llama 3.1 via Groq (free) |
| Deployment | Render.com |

---

## Files

| File | Role |
|---|---|
| `Joi.py` | Backend — LangChain RAG + Flask API + serves frontend |
| `index.html` | Frontend — chat UI |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render.com one-click deployment config |
| `.python-version` | Pins Python 3.11.9 for LangChain compatibility |
| `memories.json` | Auto-created, persists patient memories |
| `.env` | API keys (never commit to GitHub) |

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

### Step 3 — Create a `.env` file
```
GROQ_API_KEY=gsk_your_key_here
```

### Step 4 — Run
```bash
python Joi.py
```

### Step 5 — Open in browser
Go to **http://localhost:5000**

---

## 🚀 Deploy to Render

1. Push to GitHub (make sure `.env` is in `.gitignore`)
2. Go to https://render.com → **New → Web Service**
3. Connect your GitHub repo
4. Add environment variable: `GROQ_API_KEY = gsk_your_key`
5. Deploy → share your URL

**Live demo:** https://joi-alzheimer-assistant.onrender.com/

---
## License
This project is licensed under the [MIT License](LICENSE), which can be found in the LICENSE file.
## ⚠️ Disclaimer

---
Joi is a beta research project and is not a certified medical device. It is not intended to replace professional medical care or treatment for Alzheimer's disease. Always consult a qualified healthcare professional for medical advice.

---

## About

Built with ❤️ as a beta project to explore how AI can preserve human memory and improve the quality of life for Alzheimer's patients and their families.
