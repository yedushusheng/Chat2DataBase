"""
PostgreSQL 技能库
"""

from app.skills.base import BaseSkill, skill_registry


class PostgreSQLSkill(BaseSkill):
    db_type = "postgresql"
    display_name = "PostgreSQL"

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深PostgreSQL专家，熟悉PG内核、性能调优、高可用和逻辑复制。"
            "请基于PostgreSQL官方文档和最佳实践，为用户提供：\n"
            "1. 清晰的故障排查思路\n"
            "2. 可落地的实用技巧（含pg_stat、EXPLAIN、pg_dump等）\n"
            "3. 关键参数推荐及解释\n"
            "4. 完整的分步解决方案\n"
            "5. 风险避坑提示\n"
            "请优先参考知识库内容，若知识库不足再调用通用能力。"
        )


skill_registry.register(PostgreSQLSkill())
