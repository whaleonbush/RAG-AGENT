from __future__ import annotations

import hashlib
import struct
from abc import ABC, abstractmethod
from typing import List

import httpx

from project_agent.config import get_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class SimpleEmbedProvider(EmbeddingProvider):
    """외부 다운로드 없이 동작하는 간단 임베딩 (사내 환경용).

    텍스트 해시 기반으로 결정적 벡터를 생성합니다.
    의미 검색 품질은 FastEmbed/Ollama에 못 미치지만 파이프라인 검증용으로 충분합니다.
    """

    DIM = 384  # bge-small-en-v1.5 와 동일 차원

    def _text_to_vector(self, text: str) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).digest()
        # 시드를 여러 번 해시하여 차원을 채움
        vec: List[float] = []
        seed = h
        while len(vec) < self.DIM:
            seed = hashlib.sha256(seed).digest()
            # 4바이트씩 float로 변환 → [-1, 1] 범위로 정규화
            for i in range(0, len(seed), 4):
                if len(vec) >= self.DIM:
                    break
                bits = struct.unpack(">I", seed[i : i + 4])[0]
                vec.append((bits / 0xFFFFFFFF) * 2.0 - 1.0)
        # L2 정규화
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]


class FastEmbedProvider(EmbeddingProvider):
    def __init__(self) -> None:
        settings = get_settings()
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=settings.embedding_model)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[float(x) for x in v] for v in self._model.embed(texts)]


class OllamaEmbedProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _clean_text(text: str) -> str:
        """Ollama 임베딩에 실패할 수 있는 제어 문자 등을 제거합니다."""
        import re
        # 제어 문자 제거 (개행, 탭은 유지)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # 너무 긴 텍스트는 자름 (bge-m3 최대 8192 토큰)
        return text[:3000]

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        cleaned = [self._clean_text(t) for t in texts]
        batch_size = 10  # Ollama 과부하 방지
        with httpx.Client(base_url=self.settings.ollama_base_url, timeout=120.0, trust_env=False) as client:
            for i in range(0, len(cleaned), batch_size):
                batch = cleaned[i:i + batch_size]
                try:
                    resp = client.post(
                        "/api/embed",
                        json={"model": self.settings.ollama_embed_model, "input": batch},
                    )
                    resp.raise_for_status()
                    vectors.extend(resp.json()["embeddings"])
                except Exception as e:
                    print(f"[EMBED ERROR] Batch {i}-{i+len(batch)} failed: {e}")
                    # 개별 처리 폴백
                    for text in batch:
                        try:
                            resp = client.post(
                                "/api/embed",
                                json={"model": self.settings.ollama_embed_model, "input": [text]},
                            )
                            resp.raise_for_status()
                            vectors.extend(resp.json()["embeddings"])
                        except Exception as e2:
                            print(f"[EMBED ERROR] Single embed failed (len={len(text)}): {e2}")
                            # 더미 벡터로 대체 (1024차원 - bge-m3)
                            vectors.append([0.0] * 1024)
        return vectors


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "simple":
        return SimpleEmbedProvider()
    if settings.embedding_provider == "ollama":
        return OllamaEmbedProvider()
    # 기본값: 사내 환경에서 FastEmbed 다운로드가 안 되면 simple로 자동 전환
    try:
        return FastEmbedProvider()
    except Exception:
        import warnings

        warnings.warn(
            "FastEmbed 초기화 실패 — SimpleEmbedProvider로 대체합니다. "
            "의미 검색 품질이 낮을 수 있습니다.",
            stacklevel=2,
        )
        return SimpleEmbedProvider()
