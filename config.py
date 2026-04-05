from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # LLM
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: Literal["openai", "groq", "ollama"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_PROVIDER: Literal["openai", "huggingface"] = "openai"

    # News APIs
    NEWSAPI_KEY: str = ""
    GNEWS_API_KEY: str = ""

    # Vector Store
    VECTOR_STORE_PATH: str = "./data/vectorstore"
    VECTOR_STORE_TYPE: Literal["faiss", "chroma", "pinecone"] = "faiss"
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./news.db"

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    NEWS_REFRESH_INTERVAL: int = 60  # minutes
    MAX_ARTICLES_PER_SOURCE: int = 20
    RAG_TOP_K: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
