"""
文档解析模块
支持 PDF / DOCX / TXT / MD
"""

import io
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from app.core.logger import logger


class DocumentParser:
    """文档解析器"""

    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}

    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        ext = path.suffix.lower().lstrip(".")
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}")

        logger.info("parsing_document", path=file_path, type=ext)

        if ext == "pdf":
            return self._parse_pdf(file_path)
        elif ext == "docx":
            return self._parse_docx(file_path)
        else:
            return self._parse_text(file_path)

    def parse_bytes(self, filename: str, content: bytes) -> List[Document]:
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}")

        logger.info("parsing_bytes", filename=filename, size=len(content))

        if ext == "pdf":
            return self._parse_pdf_bytes(content, filename)
        elif ext == "docx":
            return self._parse_docx_bytes(content, filename)
        else:
            text = content.decode("utf-8", errors="ignore")
            return [Document(page_content=text, metadata={"source": filename})]

    def _parse_pdf(self, file_path: str) -> List[Document]:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        return loader.load()

    def _parse_pdf_bytes(self, content: bytes, filename: str) -> List[Document]:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        docs = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            docs.append(Document(page_content=text, metadata={"source": filename, "page": i + 1}))
        return docs

    def _parse_docx(self, file_path: str) -> List[Document]:
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        return loader.load()

    def _parse_docx_bytes(self, content: bytes, filename: str) -> List[Document]:
        import docx2txt
        text = docx2txt.process(io.BytesIO(content))
        return [Document(page_content=text, metadata={"source": filename})]

    def _parse_text(self, file_path: str) -> List[Document]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": file_path})]
