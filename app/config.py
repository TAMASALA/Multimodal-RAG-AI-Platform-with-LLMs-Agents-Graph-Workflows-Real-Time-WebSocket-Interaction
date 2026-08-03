"""
Centralized application configuration.
All settings are loaded from environment variables / .env file.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "multimodal-rag"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/app.db"

    # --- Storage ---
    UPLOAD_DIR: str = "./storage/uploads"
    IMAGE_DIR: str = "./storage/images"
    CACHE_DIR: str = "./storage/cache"
    FAISS_INDEX_DIR: str = "./storage/faiss"
    FAISS_INDEX_NAME: str = "index.faiss"

    # --- Embeddings ---
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_DIM: int = 384

    # --- Chunking ---
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # --- Retrieval ---
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.25

    # --- LLM (Groq) ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    GROQ_TEMPERATURE: float = 0.2
    GROQ_MAX_TOKENS: int = 1024

    # --- OCR ---
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # --- Security ---
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = ".pdf"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip().lower() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()]

    def ensure_directories(self) -> None:
        for d in [self.UPLOAD_DIR, self.IMAGE_DIR, self.CACHE_DIR, self.FAISS_INDEX_DIR]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings


settings = get_settings()
