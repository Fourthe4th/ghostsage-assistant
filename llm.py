from typing import List, Dict, Optional
import json
import requests

from openai import OpenAI
from config import settings


def _build_system_message() -> Dict[str, str]:
    return {
        "role": "system",
        "content": (
            "You are a helpful AI assistant named GhostSage. "
            "You help with coding, AI, automation, and trading.\n\n"
            "You are often given excerpts from user-uploaded documents and code files "
            "(for example Python scripts, PDFs, or text files) inside the conversation "
            "history. When the user asks about a 'file', 'code', 'script', or 'bot', "
            "you MUST assume that any provided excerpts represent that file.\n\n"
            "Important rules:\n"
            "- Never say things like 'I don't see any uploaded file' or "
            "'I don't see the code'.\n"
            "- If excerpts are present, analyze them directly and reference specific "
            "functions, variables, and behaviors.\n"
            "- If no excerpts are present, still give practical, concrete guidance "
            "based on the user's description (e.g., how to debug, what to check), "
            "and ask clarifying questions if needed.\n\n"
            "When analyzing code:\n"
            "- Summarize what the code does.\n"
            "- Point out potential bugs, edge cases, and risky assumptions.\n"
            "- Suggest improvements to structure, error-handling, logging, and "
            "performance.\n"
            "- Be concrete and actionable."
        ),
    }


# ---------- OpenAI backend ----------

_openai_client: Optional[OpenAI] = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set, but model_backend is 'openai'. "
                "Set it in your .env file."
            )
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


def _chat_openai(messages: List[Dict[str, str]]) -> str:
    client = _get_openai_client()

    # Ensure a system prompt exists
    if not messages or messages[0].get("role") != "system":
        messages = [_build_system_message()] + messages

    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.25,
    )
    return completion.choices[0].message.content


# ---------- Local HTTP backend (Ollama / custom server) ----------

def _chat_local(messages: List[Dict[str, str]]) -> str:
    """
    Call a local chat completion server (e.g. Ollama) via HTTP.

    Expects an OpenAI-compatible /v1/chat/completions endpoint:
    - URL: settings.local_model_base_url
    - Model name: settings.local_model_name
    """
    if not settings.local_model_base_url:
        raise RuntimeError("LOCAL_MODEL_BASE_URL is not configured for local backend.")
    if not settings.local_model_name:
        raise RuntimeError("LOCAL_MODEL_NAME is not configured for local backend.")

    # Ensure a system prompt exists
    if not messages or messages[0].get("role") != "system":
        messages = [_build_system_message()] + messages

    payload = {
        "model": settings.local_model_name,
        "messages": messages,
        "temperature": 0.25,
    }

    try:
        resp = requests.post(
            settings.local_model_base_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60,
        )
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Local model request failed: {e}")

    try:
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Failed to parse local model response as JSON: {e}")

    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Unexpected local model response format: {e}")


# ---------- Public entrypoint ----------

def chat(messages: List[Dict[str, str]]) -> str:
    """
    Dispatch chat call to the selected backend.

    Backends:
    - 'openai': OpenAI Chat Completions API (default)
    - 'local' : Local HTTP server (Ollama or compatible)
    """
    backend = (settings.model_backend or "openai").lower()

    if backend == "openai":
        return _chat_openai(messages)
    elif backend == "local":
        return _chat_local(messages)
    else:
        raise RuntimeError(
            f"Unknown MODEL_BACKEND '{settings.model_backend}'. "
            "Use 'openai' or 'local' in your .env."
        )
