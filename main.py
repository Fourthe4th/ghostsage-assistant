from typing import List
import uuid
import re

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from models import ConversationMessage
from schemas import ChatRequest, ChatResponse, Message
import llm
from webscraper import fetch_url

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal AI Assistant")

# CORS (open for now; can tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_history(db: Session, session_id: str) -> List[ConversationMessage]:
    return (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.id.asc())
        .all()
    )


def save_message(db: Session, session_id: str, role: str, content: str) -> ConversationMessage:
    msg = ConversationMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


URL_PATTERN = re.compile(r"https?://\S+")


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Create new session if none provided
    session_id = request.session_id or str(uuid.uuid4())

    # Load history from DB
    history_rows = get_history(db, session_id)
    history_messages = [{"role": m.role, "content": m.content} for m in history_rows]

    # 🔎 Simple web scraping: if the user includes URLs, fetch & inject their content
    urls = URL_PATTERN.findall(request.message)
    for url in urls[:3]:  # safety: limit to first 3 URLs
        scraped = fetch_url(url)
        # Inject scraped content as an extra user message BEFORE their question
        history_messages.append(
            {
                "role": "user",
                "content": f"Here is live content fetched from {url}:\n\n{scraped}",
            }
        )

    # Append the actual user message
    history_messages.append({"role": "user", "content": request.message})

    # Call LLM
    try:
        reply = llm.chat(history_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    # Persist both messages
    save_message(db, session_id, "user", request.message)
    save_message(db, session_id, "assistant", reply)

    # Reload full history after save
    new_history = get_history(db, session_id)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        history=[Message(role=m.role, content=m.content) for m in new_history],
    )


# Serve static frontend (simple chat page)
app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static",
)
