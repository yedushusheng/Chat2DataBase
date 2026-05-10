"""
TiDB 技能库
"""

from app.skills.base import BaseSkill, skill_registry


class TiDBSkill(BaseSkill):
    db_type = "tidb"
    display_name = "TiDB"

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深TiDB专家，熟悉TiDB分布式架构、TiKV、PD、TiDB Dashboard和TiUP。"
            "请基于TiDB官方文档和最佳实践，为用户提供：\n"
            "1. 清晰的故障排查思路\n"
            "2. 可落地的实用技巧（含Dashboard、Grafana、tiup等）\n"
            "3. 关键参数推荐及解释\n"
            "4. 完整的分步解决方案\n"
            "5. 风险避坑提示\n"
            "请优先参考知识库内容，若知识库不足再调用通用能力。"
        )


skill_registry.register(TiDBSkill())
