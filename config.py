from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI config
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    # Embeddings (for RAG)
    embedding_model: str = "text-embedding-3-small"

    # Backend selection: "openai" or "local"
    model_backend: str = "openai"

    # Local model config (for future use, e.g. Ollama / custom server)
    local_model_name: str = "llama3"
    local_model_base_url: str = "http://localhost:11434/v1/chat/completions"

    # DB config
    database_url: str = "sqlite:///./assistant.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
