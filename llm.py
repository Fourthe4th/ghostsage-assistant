from typing import List, Dict
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.openai_api_key)


def chat(messages: List[Dict[str, str]]) -> str:
    """
    Call the LLM with a conversation history.
    messages: list of {"role": "user"|"assistant"|"system", "content": str}
    """

    # Ensure a system prompt exists
    if not messages or messages[0].get("role") != "system":
        system_msg = {
            "role": "system",
            "content": (
                "You are a helpful AI assistant named GhostSage. "
                "You help with coding, AI, automation, and trading. "
                "Be clear, concise, and practical."
            ),
        }
        messages = [system_msg] + messages

    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.2,
    )

    return completion.choices[0].message.content
