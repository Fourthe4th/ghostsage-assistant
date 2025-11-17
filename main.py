from typing import List
import uuid
import re

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from models import ConversationMessage
from schemas import ChatRequest, ChatResponse, Message
import llm
from webscraper import fetch_url
from rag import ingest_uploaded_file, query_relevant_chunks

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
CODE_QUESTION_PATTERN = re.compile(
    r"\b(code|script|file|py|bot|bug|debug|refactor|function|class|module)\b",
    re.IGNORECASE,
)


# ---------- File upload endpoint (RAG ingestion) ----------

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (PDF or text) and ingest it into the vector store.
    """
    try:
        file_bytes = await file.read()
        num_chunks = ingest_uploaded_file(file_bytes, file.filename)
        if num_chunks == 0:
            return {
                "filename": file.filename,
                "status": "no_content",
                "message": "No usable text extracted from file.",
            }
        return {
            "filename": file.filename,
            "status": "ok",
            "chunks_indexed": num_chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload/ingest error: {e}")


# ---------- Chat endpoint ----------

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Create new session if none provided
    session_id = request.session_id or str(uuid.uuid4())

    # Load history from DB
    history_rows = get_history(db, session_id)
    history_messages = [{"role": m.role, "content": m.content} for m in history_rows]

    user_query = request.message.strip()

    # 🔎 RAG: query vector store for relevant document chunks
    rag_chunks = query_relevant_chunks(user_query, top_k=5)
    if rag_chunks:
        context_parts = []
        first_filename = None
        for chunk_text, meta in rag_chunks:
            src = meta.get("filename", "uploaded document")
            if first_filename is None:
                first_filename = src
            context_parts.append(f"[Source: {src}]\n{chunk_text}")

        rag_context = "\n\n---\n\n".join(context_parts)

        # If this looks like a code/file question, be explicit
        if CODE_QUESTION_PATTERN.search(user_query):
            history_messages.append(
                {
                    "role": "user",
                    "content": (
                        "You are analyzing the user's uploaded document or code file. "
                        f"The file name appears to be: {first_filename or 'unknown'}.\n\n"
                        "Below are relevant excerpts from that file. "
                        "The user is asking you to analyze this code for bugs, risky "
                        "assumptions, and improvements. Focus your answer on this code.\n\n"
                        f"{rag_context}"
                    ),
                }
            )
        else:
            history_messages.append(
                {
                    "role": "user",
                    "content": (
                        "Here are relevant excerpts from previously uploaded documents. "
                        "Use them as context when answering the next question:\n\n"
                        f"{rag_context}"
                    ),
                }
            )

    # 🔎 Simple web scraping: if the user includes URLs, fetch & inject their content
    urls = URL_PATTERN.findall(user_query)
    for url in urls[:3]:  # safety: limit to first 3 URLs
        scraped = fetch_url(url)
        history_messages.append(
            {
                "role": "user",
                "content": f"Here is live content fetched from {url}:\n\n{scraped}",
            }
        )

    # Append the actual user message
    history_messages.append({"role": "user", "content": user_query})

    # Call LLM
    try:
        reply = llm.chat(history_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    # Persist both messages
    save_message(db, session_id, "user", user_query)
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
