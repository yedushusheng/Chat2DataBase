"""
数据库管理接口
- GET /api/databases                列出支持的数据库
- GET /api/databases/{db_type}/skills  查看某数据库技能分类
"""

from fastapi import APIRouter

from app.config import settings
from app.core.response import ResponseModel
from app.skills.base import skill_registry

db_router = APIRouter(prefix="/api/databases", tags=["数据库"])


@db_router.get("", response_model=ResponseModel)
async def list_databases():
    """获取支持的数据库列表"""
    return ResponseModel.success(data=settings.databases)


@db_router.get("/{db_type}/skills", response_model=ResponseModel)
async def get_skill_categories(db_type: str):
    """获取某数据库的技能分类"""
    skill = skill_registry.get(db_type)
    if not skill:
        return ResponseModel.error(code=404, message="该数据库暂无技能库")
    return ResponseModel.success(
        data={"db_type": db_type, "name": skill.display_name, "categories": skill.get_all_categories()}
    )
