"""
Chroma向量存储封装
负责文档向量化、存储、检索、删除、统计
"""

import hashlib
from typing import List, Optional

import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from app.config import settings
from app.core.logger import logger
from app.rag.embeddings import get_embedding_manager
from app.rag.chunker import DocumentChunker


class ChromaStore:
    """Chroma向量数据库封装"""

    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.collection_name = settings.CHROMA_COLLECTION
        self.embedding = get_embedding_manager()
        self.chunker = DocumentChunker()

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embedding._model,
        )

    def add_documents(self, docs: List[Document], db_type: str = "general") -> int:
        """添加文档到向量库"""
        if not docs:
            return 0

        chunks = self.chunker.split(docs)

        # 去重
        unique_chunks = []
        seen_hashes = set()
        for chunk in chunks:
            h = hashlib.md5(chunk.page_content.encode()).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                chunk.metadata["db_type"] = db_type
                chunk.metadata["chunk_hash"] = h
                unique_chunks.append(chunk)

        if not unique_chunks:
            return 0

        self.vectorstore.add_documents(unique_chunks)
        logger.info("documents_added", db_type=db_type, original_docs=len(docs), chunks=len(unique_chunks))
        return len(unique_chunks)

    def search(
        self,
        query: str,
        db_type: Optional[str] = None,
        top_k: int = None,
        score_threshold: float = None,
    ) -> List[Document]:
        """相似度检索"""
        rag_cfg = settings.rag_config
        k = top_k or rag_cfg.get("top_k", 5)
        threshold = score_threshold or rag_cfg.get("score_threshold", 0.65)

        filter_dict = {"db_type": db_type} if db_type else None

        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query, k=k * 2, filter=filter_dict
            )
        except Exception as e:
            logger.error("chroma_search_failed", error=str(e))
            return []

        filtered = [doc for doc, score in results if score >= threshold]
        logger.info("chroma_searched", query=query[:50], db_type=db_type, results=len(filtered))
        return filtered[:k]

    def delete_by_source(self, source: str) -> int:
        try:
            self.vectorstore._collection.delete(where={"source": source})
            logger.info("documents_deleted", source=source)
            return 1
        except Exception as e:
            logger.error("delete_failed", source=source, error=str(e))
            return 0

    def list_sources(self) -> List[str]:
        try:
            data = self.vectorstore._collection.get(include=["metadatas"])
            sources = set()
            for meta in data.get("metadatas", []):
                if meta and "source" in meta:
                    sources.add(meta["source"])
            return sorted(list(sources))
        except Exception as e:
            logger.error("list_sources_failed", error=str(e))
            return []

    def get_stats(self) -> dict:
        try:
            count = self.vectorstore._collection.count()
            return {"collection": self.collection_name, "total_documents": count, "persist_directory": self.persist_dir}
        except Exception as e:
            logger.error("stats_failed", error=str(e))
            return {"collection": self.collection_name, "total_documents": 0}


_chroma_store: Optional[ChromaStore] = None


def get_chroma_store() -> ChromaStore:
    global _chroma_store
    if _chroma_store is None:
        _chroma_store = ChromaStore()
    return _chroma_store
