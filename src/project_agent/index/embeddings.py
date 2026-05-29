from __future__ import annotations

import hashlib
import struct
from abc import ABC, abstractmethod
from typing import List, Optional

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

        # threads를 지정하면 CPU 코어를 활용해 임베딩이 빨라진다.
        kwargs: dict = {"model_name": settings.embedding_model}
        if settings.embedding_threads > 0:
            kwargs["threads"] = settings.embedding_threads
        self._model = TextEmbedding(**kwargs)
        self._batch_size = settings.embedding_batch_size

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [
            [float(x) for x in v]
            for v in self._model.embed(texts, batch_size=self._batch_size)
        ]


class OllamaEmbedProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        # 연결을 재사용 + trust_env=False로 사내 프록시 간섭 방지.
        self._client = httpx.Client(
            base_url=self.settings.ollama_base_url, timeout=120.0, trust_env=False
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        """Ollama 임베딩에 실패할 수 있는 제어 문자 등을 제거합니다."""
        import re

        # 제어 문자 제거 (개행, 탭은 유지)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # 너무 긴 텍스트는 자름 (bge-m3 최대 8192 토큰)
        return text[:3000]

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        cleaned = [self._clean_text(t) for t in texts]
        batch_size = self.settings.embedding_batch_size  # 배치 임베딩으로 호출 수 감소
        for i in range(0, len(cleaned), batch_size):
            batch = cleaned[i : i + batch_size]
            try:
                resp = self._client.post(
                    "/api/embed",
                    json={
                        "model": self.settings.ollama_embed_model,
                        "input": batch,
                        "keep_alive": self.settings.ollama_keep_alive,
                    },
                )
                resp.raise_for_status()
                vectors.extend(resp.json()["embeddings"])
            except Exception as e:
                print(f"[EMBED ERROR] Batch {i}-{i + len(batch)} failed: {e}")
                # 개별 처리 폴백
                for text in batch:
                    try:
                        resp = self._client.post(
                            "/api/embed",
                            json={
                                "model": self.settings.ollama_embed_model,
                                "input": [text],
                                "keep_alive": self.settings.ollama_keep_alive,
                            },
                        )
                        resp.raise_for_status()
                        vectors.extend(resp.json()["embeddings"])
                    except Exception as e2:
                        print(f"[EMBED ERROR] Single embed failed (len={len(text)}): {e2}")
                        # 더미 벡터로 대체 (1024차원 - bge-m3)
                        vectors.append([0.0] * 1024)
        return vectors


_provider: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """임베딩 모델은 로드 비용이 크므로 프로세스당 1회만 생성해 재사용한다."""
    global _provider
    if _provider is not None:
        return _provider

    settings = get_settings()
    if settings.embedding_provider == "simple":
        _provider = SimpleEmbedProvider()
    elif settings.embedding_provider == "ollama":
        _provider = OllamaEmbedProvider()
    else:
        # 기본값: 사내 환경에서 FastEmbed 다운로드가 안 되면 simple로 자동 전환
        try:
            _provider = FastEmbedProvider()
        except Exception:
            import warnings

            warnings.warn(
                "FastEmbed 초기화 실패 — SimpleEmbedProvider로 대체합니다. "
                "의미 검색 품질이 낮을 수 있습니다.",
                stacklevel=2,
            )
            _provider = SimpleEmbedProvider()
    return _provider
