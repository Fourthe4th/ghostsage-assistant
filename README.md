# GhostSage – Personal AI Assistant (v0.1)

GhostSage is a **personal AI assistant** built with **FastAPI + OpenAI + SQLite**, with a simple web UI and **live web scraping**.

It runs locally (WSL/Linux/macOS), gives ChatGPT-style conversational responses, remembers your conversation history per session, and can fetch + summarize content from any URL you paste.

---

## ✨ Features

- 🧠 **ChatGPT-style assistant** using OpenAI Chat Completions  
- 🗂 **Persistent conversation history** in SQLite per session  
- 🌐 **Built-in web scraper** – paste any URL, get a summarized answer using the live page content  
- 💾 Runs locally with **FastAPI** and **Uvicorn**  
- 🌍 Simple HTML/CSS front-end served as static files (no Node required)  
- 🔐 API keys managed via `.env` (not committed to Git)

---

## 🏗 Tech Stack

- **Backend:** FastAPI, Uvicorn  
- **LLM:** OpenAI Chat Completions (e.g. `gpt-4.1-mini`)  
- **Database:** SQLite (`assistant.db`) via SQLAlchemy  
- **Frontend:** Static HTML/CSS/JS (served by FastAPI `StaticFiles`)  
- **Web Scraping:** `requests` + `BeautifulSoup4`  

---

## 📁 Project Structure

```text
.
├── main.py            # FastAPI app (chat endpoint, web scraper integration)
├── llm.py             # LLM wrapper (OpenAI Chat API)
├── webscraper.py      # URL fetch + HTML cleanup helper
├── config.py          # Settings / env loader
├── db.py              # Database engine + session
├── models.py          # SQLAlchemy ORM models (ConversationMessage)
├── schemas.py         # Pydantic models (request/response)
├── static/
│   └── index.html     # Web UI (chat page)
├── assistant.db       # SQLite DB (created at runtime, ignored by git)
├── .env               # Secrets (OpenAI key, model name) – not committed
├── .gitignore         # Ignore venv, db, compiled files, env
└── README.md
