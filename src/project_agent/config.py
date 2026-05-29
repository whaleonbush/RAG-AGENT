from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: Path = Path("./storage")

    embedding_provider: str = "fastembed"  # fastembed | ollama | simple
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    # 0이면 fastembed 기본값(=CPU 코어 수) 사용. 명시하면 그 수의 스레드로 임베딩.
    embedding_threads: int = 0
    embedding_batch_size: int = 32

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"
    # 모델을 메모리에 유지하는 시간. CPU 환경에서 재로딩을 막아 응답을 크게 단축한다.
    ollama_keep_alive: str = "30m"
    # 컨텍스트 창 토큰 수(작을수록 빠름).
    ollama_num_ctx: int = 4096
    # 답변 최대 생성 토큰 수(작을수록 빠름).
    ollama_num_predict: int = 512

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
