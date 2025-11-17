from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    database_url: str = "sqlite:///./assistant.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
