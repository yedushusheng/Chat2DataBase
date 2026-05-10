"""
Embedding模型封装
使用 sentence-transformers 生成文本向量
"""

from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings
from app.core.logger import logger


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
        self._model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("embedding_model_loaded")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)


def get_embedding_manager() -> EmbeddingManager:
    return EmbeddingManager()
