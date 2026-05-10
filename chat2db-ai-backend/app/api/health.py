"""
健康检查与系统状态接口
"""

from fastapi import APIRouter

from app.core.response import ResponseModel
from app.rag.chroma_store import get_chroma_store
from app.skills.base import skill_registry

health_router = APIRouter(prefix="/api/health", tags=["健康检查"])


@health_router.get("", response_model=ResponseModel)
async def health():
    return ResponseModel.success(data={"status": "ok", "service": "chat2db-ai"})


@health_router.get("/stats", response_model=ResponseModel)
async def system_stats():
    store = get_chroma_store()
    return ResponseModel.success(data={
        "rag": store.get_stats(),
        "skills": skill_registry.list_skills(),
    })
