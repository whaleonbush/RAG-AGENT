from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: Path = Path("./storage")

    embedding_provider: str = "fastembed"  # fastembed | ollama
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"

    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_top_k: int = 6

    @property
    def projects_dir(self) -> Path:
        return self.data_dir / "projects"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.data_dir.mkdir(parents=True, exist_ok=True)
        _settings.projects_dir.mkdir(parents=True, exist_ok=True)
        _settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return _settings
