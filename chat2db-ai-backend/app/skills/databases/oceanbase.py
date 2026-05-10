"""
OceanBase 技能库
"""

from app.skills.base import BaseSkill, skill_registry


class OceanBaseSkill(BaseSkill):
    db_type = "oceanbase"
    display_name = "OceanBase"

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深OceanBase专家，熟悉OceanBase分布式架构、OBProxy、OCP和OBServer。"
            "请基于OceanBase官方文档和最佳实践，为用户提供：\n"
            "1. 清晰的故障排查思路\n"
            "2. 可落地的实用技巧（含OCP、Grafana、clog、slog等）\n"
            "3. 关键参数推荐及解释\n"
            "4. 完整的分步解决方案\n"
            "5. 风险避坑提示\n"
            "请优先参考知识库内容，若知识库不足再调用通用能力。"
        )


skill_registry.register(OceanBaseSkill())
