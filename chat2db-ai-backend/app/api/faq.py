"""
FAQ接口
- GET /api/faq/hot     高频问题
- GET /api/faq/search  搜索FAQ
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.response import ResponseModel
from app.skills.base import skill_registry

faq_router = APIRouter(prefix="/api/faq", tags=["FAQ"])


@faq_router.get("/hot", response_model=ResponseModel)
async def hot_faq(
    db_type: Optional[str] = Query(default=None, description="按数据库类型过滤"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """获取高频问题列表"""
    results = []
    if db_type:
        skill = skill_registry.get(db_type)
        if skill:
            results = skill.get_hot_topics(limit=limit)
    else:
        for skill_info in skill_registry.list_skills():
            s = skill_registry.get(skill_info["db_type"])
            if s:
                results.extend(s.get_hot_topics(limit=limit // max(len(skill_registry.list_skills()), 1) + 1))

    seen = set()
    unique = []
    for r in results:
        key = r.get("id") or r.get("title")
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    return ResponseModel.success(data=unique[:limit])


@faq_router.get("/search", response_model=ResponseModel)
async def search_faq(
    q: str = Query(..., description="搜索关键词"),
    db_type: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
):
    """搜索FAQ/技能库"""
    results = []
    if db_type:
        skill = skill_registry.get(db_type)
        if skill:
            results = skill.search(q)
    else:
        for skill_info in skill_registry.list_skills():
            s = skill_registry.get(skill_info["db_type"])
            if s:
                results.extend(s.search(q))

    data = []
    for r in results[:limit]:
        data.append({
            "db_type": r.db_type,
            "category": r.category,
            "title": r.title,
            "content": r.content[:300] + "..." if len(r.content) > 300 else r.content,
            "confidence": r.confidence,
        })
    return ResponseModel.success(data=data)
