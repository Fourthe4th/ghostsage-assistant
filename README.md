# GhostSage – Personal AI Assistant (v0.2)

GhostSage is a **local personal AI assistant** built with **FastAPI + OpenAI + ChromaDB + SQLite**, featuring:

- ChatGPT-style conversational interface
- Live web-scraping for URL summaries
- Local RAG (Retrieval-Augmented Generation)
- Code ingestion + semantic search
- Persistent conversation history per session
- Lightweight HTML/JS front-end served directly by FastAPI

This project is designed as a **portfolio-grade AI developer showcase** that demonstrates backend engineering, AI integration, vector databases, and production-style structure.

---

## ✨ Features

- 🧠 **ChatGPT-style assistant** using OpenAI Chat Completions  
- 🗂 **Local RAG vector DB** via ChromaDB + SentenceTransformers embeddings  
- 📄 **File ingestion** (TXT/PDF/code) with semantic chunking  
- 🧩 **Code analysis mode** – ask questions about uploaded scripts  
- 🌐 **Live web scraper** – fetch and summarize any URL  
- 💾 **Persistent SQLite history** per conversation  
- ⚡ **FastAPI backend + static HTML/JS frontend**  
- 🔐 API secrets via `.env`  
- 🧪 **Pytest test suite** (health checks)

---

## 🏗 Tech Stack

**Backend:** FastAPI, Uvicorn  
**AI Model:** OpenAI Chat Completions  
**RAG Engine:** ChromaDB  
**Embeddings:** SentenceTransformers (`all-MiniLM-L6-v2`)  
**Database:** SQLite + SQLAlchemy  
**Frontend:** Static HTML/CSS/JS  
**Web Scraping:** requests + BeautifulSoup4  
**Testing:** pytest + TestClient  

---

## 📁 Project Structure

├── main.py # FastAPI app: chat, upload, scrape, RAG query
├── llm.py # OpenAI API wrapper
├── rag.py # Vector DB: embedding, ingestion, retrieval
├── webscraper.py # Live URL scraper with HTML cleanup
├── db.py # SQLite engine + session
├── models.py # SQLAlchemy ORM models
├── schemas.py # Pydantic schemas
├── config.py # Settings loader (.env)
├── static/
│ ├── index.html
│ ├── styles.css
│ └── script.js
├── tests/
│ ├── conftest.py
│ └── test_health.py
├── assistant.db # Created at runtime
├── requirements.txt
└── README.md

---

## 🚀 Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/Fourthe4th/ghostsage-assistant.git
cd ghostsage-assistant
2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Add .env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini

5. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000


Visit: http://localhost:8000

📥 RAG: Upload Files + Ask Questions

Upload TXT, PDF, or code files:

GhostSage chunks + embeds them into Chroma

You can ask:
"Summarize this"
"Find bugs"
"Explain this trading strategy"

🌐 URL Scraping

Paste any URL:

GhostSage fetches HTML

Cleans the text

Summarizes it and answers questions about the page

🧪 Testing

This project includes basic API tests using pytest.

Run the test suite:

pytest


Tests live in the tests/ directory.

📌 Roadmap (v0.3 → v1.0)

 Next.js front-end UI

 Chat history sidebar

 Local model support (Ollama)

 Streaming responses (SSE)

 Multiple conversations

 Better PDF parsing

 Code execution sandbox

GhostSage demonstrates:

AI integration

Vector search / RAG

Web scraping

Backend engineering

Database modeling

Testing

Clean architecture



📬 Contact

If you'd like to reach me for collaboration or opportunities:

Email: fourthe4th@gmail.com
