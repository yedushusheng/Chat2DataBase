"""
Embedding模型封装
使用 sentence-transformers 生成文本向量
"""

import os
from typing import List

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_ENDPOINT", "https://hf-mirror.com")

from langchain_core.embeddings import Embeddings

from app.config import settings
from app.core.logger import logger


class MockEmbeddings(Embeddings):
    """当HuggingFace模型不可用时使用的mock embedding，返回零向量"""

    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dim for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.0] * self.dim


class EmbeddingManager:
    """向量嵌入管理器（单例）"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is not None:
            return
        model_name = settings.EMBEDDING_MODEL
        logger.info("loading_embedding_model", model=model_name)
        self._model = MockEmbeddings()
        logger.info("embedding_model_loaded (mock)")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)


def get_embedding_manager() -> EmbeddingManager:
    return EmbeddingManager()
