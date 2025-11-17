from typing import List, Tuple
from io import BytesIO
import uuid

import chromadb
from chromadb.config import Settings as ChromaSettings
from pypdf import PdfReader

# NEW: Local embedding model
from sentence_transformers import SentenceTransformer


# ───────────────────────────────
# Local Embedding Model (FREE)
# ───────────────────────────────
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_texts(input: List[str]) -> List[List[float]]:
    """
    Local embedding function using all-MiniLM-L6-v2.
    """
    embeddings = _model.encode(input, convert_to_numpy=True).tolist()
    return embeddings


class LocalEmbeddingFunction:
    """
    Chroma embedding function wrapper for local embeddings.
    """

    def __call__(self, input: List[str]) -> List[List[float]]:
        return embed_texts(input)

    def name(self) -> str:
        return "local-all-MiniLM-L6-v2"


# ───────────────────────────────
# ChromaDB Persistent Client
# ───────────────────────────────
_chroma_client = chromadb.PersistentClient(
    path="chroma_db",
    settings=ChromaSettings(anonymized_telemetry=False),
)

_embedding_fn = LocalEmbeddingFunction()

_collection = _chroma_client.get_or_create_collection(
    name="ghostsage_docs",
    embedding_function=_embedding_fn,
)


# ───────────────────────────────
# PDF + Text Extraction
# ───────────────────────────────
def _extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            texts.append(txt.strip())
    return "\n\n".join(texts)


def _extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return _extract_text_from_pdf(file_bytes)
    return file_bytes.decode("utf-8", errors="ignore")


# ───────────────────────────────
# Chunking Logic
# ───────────────────────────────
def _chunk_text(text: str, chunk_size=900, overlap=150):
    if not text:
        return []
    text = text.replace("\r", "")
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
    return chunks


# ───────────────────────────────
# RAG Public Methods
# ───────────────────────────────
def ingest_uploaded_file(file_bytes: bytes, filename: str) -> int:
    raw_text = _extract_text_from_bytes(file_bytes, filename)
    if not raw_text.strip():
        return 0

    chunks = _chunk_text(raw_text)
    if not chunks:
        return 0

    doc_id = str(uuid.uuid4())
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "filename": filename, "chunk": i} for i in range(len(chunks))]

    _collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas
    )

    return len(chunks)


def query_relevant_chunks(query: str, top_k=5):
    try:
        result = _collection.query(
            query_texts=[query],
            n_results=top_k,
        )
    except Exception:
        return []

    docs = result.get("documents") or [[]]
    metas = result.get("metadatas") or [[]]

    out = []
    for chunk, meta in zip(docs[0], metas[0]):
        out.append((chunk, meta))
    return out
