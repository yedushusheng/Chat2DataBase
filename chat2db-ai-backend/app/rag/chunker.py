"""
文本分块模块
基于 RecursiveCharacterTextSplitter，针对中文优化分隔符
"""

from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.logger import logger


class DocumentChunker:
    """文档分块器"""

    def __init__(self):
        rag_cfg = settings.rag_config
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=rag_cfg.get("chunk_size", 512),
            chunk_overlap=rag_cfg.get("chunk_overlap", 128),
            separators=["\n\n", "\n", "。", "；", " ", ""],
            length_function=len,
        )

    def split(self, docs: List[Document]) -> List[Document]:
        """将文档分割为chunk"""
        if not docs:
            return []
        chunks = self.splitter.split_documents(docs)
        logger.info("document_chunked", original=len(docs), chunks=len(chunks))
        return chunks
