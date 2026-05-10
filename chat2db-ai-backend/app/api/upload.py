"""
文档上传接口
- POST   /api/upload            单文件/批量上传并解析入库
- GET    /api/upload/list       查看已入库文档
- DELETE /api/upload/{filename} 删除文档
"""

from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, UploadFile

from app.config import settings
from app.core.exceptions import BadRequestException
from app.core.logger import logger
from app.core.response import ResponseModel
from app.rag.chroma_store import get_chroma_store
from app.rag.document_parser import DocumentParser

upload_router = APIRouter(prefix="/api/upload", tags=["文档上传"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = set(settings.ALLOWED_EXTENSIONS)
MAX_SIZE = settings.MAX_UPLOAD_SIZE


@upload_router.post("", response_model=ResponseModel)
async def upload_file(
    file: UploadFile = File(...),
    db_type: str = Form(default="general"),
):
    """上传故障分析文档，解析后存入RAG知识库"""
    if not file.filename:
        raise BadRequestException("文件名不能为空")
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED:
        raise BadRequestException(f"不支持的文件类型: {ext}，仅支持 {ALLOWED}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise BadRequestException(f"文件过大，最大允许 {MAX_SIZE / 1024 / 1024}MB")

    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content)

    parser = DocumentParser()
    try:
        docs = parser.parse_bytes(file.filename, content)
    except Exception as e:
        logger.error("parse_failed", filename=file.filename, error=str(e))
        raise BadRequestException(f"文档解析失败: {str(e)}")

    store = get_chroma_store()
    chunk_count = store.add_documents(docs, db_type=db_type)

    logger.info("upload_success", filename=file.filename, db_type=db_type, chunks=chunk_count)
    return ResponseModel.success(
        data={"filename": file.filename, "db_type": db_type, "chunks": chunk_count, "size": len(content)},
        message="上传成功，已解析入库",
    )


@upload_router.post("/batch", response_model=ResponseModel)
async def upload_batch(
    files: List[UploadFile] = File(...),
    db_type: str = Form(default="general"),
):
    """批量上传文档"""
    results = []
    for file in files:
        if not file.filename:
            continue
        ext = Path(file.filename).suffix.lower().lstrip(".")
        if ext not in ALLOWED:
            results.append({"filename": file.filename, "status": "skip", "reason": "unsupported_type"})
            continue
        content = await file.read()
        if len(content) > MAX_SIZE:
            results.append({"filename": file.filename, "status": "skip", "reason": "too_large"})
            continue
        save_path = UPLOAD_DIR / file.filename
        with open(save_path, "wb") as f:
            f.write(content)
        try:
            docs = DocumentParser().parse_bytes(file.filename, content)
            chunk_count = get_chroma_store().add_documents(docs, db_type=db_type)
            results.append({"filename": file.filename, "status": "success", "chunks": chunk_count})
        except Exception as e:
            results.append({"filename": file.filename, "status": "fail", "reason": str(e)})
    return ResponseModel.success(data=results, message="批量上传完成")


@upload_router.get("/list", response_model=ResponseModel)
async def list_uploads():
    store = get_chroma_store()
    return ResponseModel.success(data={"sources": store.list_sources(), "stats": store.get_stats()})


@upload_router.delete("/{filename}", response_model=ResponseModel)
async def delete_upload(filename: str):
    store = get_chroma_store()
    count = store.delete_by_source(filename)
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
    return ResponseModel.success(data={"deleted": count}, message="删除成功")
