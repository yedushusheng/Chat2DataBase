"""
Skills 技能库基础框架
每个数据库类型对应一个 Skill 类，提供：
- 故障排查思路 (troubleshooting)
- 实用技巧 (tips)
- 参数推荐 (parameters)
- 解决方案 (solution)
- SQL示例 (sql_examples)
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.logger import logger


@dataclass
class SkillResult:
    """技能返回结果"""

    db_type: str
    category: str          # troubleshooting | tips | parameters | solution | sql_examples
    title: str
    content: str
    confidence: float = 1.0
    source: str = "skills"
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseSkill(ABC):
    """数据库技能基类"""

    db_type: str = "base"
    display_name: str = "基础数据库"

    def __init__(self):
        self.skill_dir = settings.skills_dir / self.db_type
        self._knowledge: Dict[str, List[Dict]] = {}
        self._load_skills()

    def _load_skills(self):
        """从 skills_data/{db_type}/ 加载结构化知识"""
        if not self.skill_dir.exists():
            logger.warning("skill_dir_not_found", db_type=self.db_type, path=str(self.skill_dir))
            return

        for file_path in self.skill_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    category = file_path.stem
                    self._knowledge[category] = data if isinstance(data, list) else [data]
            except Exception as e:
                logger.error("load_skill_failed", file=str(file_path), error=str(e))

    @abstractmethod
    def get_system_prompt(self) -> str:
        """返回该数据库专属系统提示词"""
        pass

    def search(self, query: str, category: Optional[str] = None) -> List[SkillResult]:
        """
        基于关键词在技能库中搜索
        简单实现：子串匹配 + 标题匹配
        """
        results = []
        query_lower = query.lower()
        categories = [category] if category else self._knowledge.keys()

        for cat in categories:
            items = self._knowledge.get(cat, [])
            for item in items:
                title = item.get("title", "")
                content = item.get("content", "")
                text = f"{title} {content}".lower()

                score = 0.0
                if query_lower in title.lower():
                    score += 0.5
                if query_lower in text:
                    score += 0.3

                if score > 0:
                    results.append(
                        SkillResult(
                            db_type=self.db_type,
                            category=cat,
                            title=title,
                            content=content,
                            confidence=min(score, 1.0),
                            source="skills",
                            metadata=item.get("metadata", {}),
                        )
                    )

        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:10]

    def get_all_categories(self) -> List[str]:
        return list(self._knowledge.keys())

    def get_hot_topics(self, limit: int = 10) -> List[Dict[str, str]]:
        """获取高频主题"""
        topics = []
        for cat, items in self._knowledge.items():
            for item in items[:limit]:
                topics.append({
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "category": cat,
                    "db_type": self.db_type,
                })
        return topics[:limit]


class SkillRegistry:
    """技能注册中心"""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill):
        self._skills[skill.db_type] = skill
        logger.info("skill_registered", db_type=skill.db_type, name=skill.display_name)

    def get(self, db_type: str) -> Optional[BaseSkill]:
        return self._skills.get(db_type)

    def list_skills(self) -> List[Dict[str, str]]:
        return [
            {"db_type": s.db_type, "name": s.display_name}
            for s in self._skills.values()
        ]


skill_registry = SkillRegistry()
