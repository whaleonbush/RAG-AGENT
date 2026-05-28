from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import httpx
from fastembed import TextEmbedding

from project_agent.config import get_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class FastEmbedProvider(EmbeddingProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._model = TextEmbedding(model_name=settings.embedding_model)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[float(x) for x in v] for v in self._model.embed(texts)]


class OllamaEmbedProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        with httpx.Client(base_url=self.settings.ollama_base_url, timeout=120.0) as client:
            for text in texts:
                resp = client.post(
                    "/api/embeddings",
                    json={"model": self.settings.ollama_embed_model, "prompt": text},
                )
                resp.raise_for_status()
                vectors.append(resp.json()["embedding"])
        return vectors


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "ollama":
        return OllamaEmbedProvider()
    return FastEmbedProvider()
