"""
自研数据库 技能库
该数据库完全依赖内部RAG文档 + Skills技能库 + Claude深度推理
不路由到通用外部模型（豆包/文心/DeepSeek/GPT）
"""

from app.skills.base import BaseSkill, skill_registry


class SelfDBSkill(BaseSkill):
    db_type = "self_db"
    display_name = "自研数据库"

    def get_system_prompt(self) -> str:
        return (
            "你是公司自研数据库的内部技术支持专家，拥有最高级别的内部知识访问权限。\n"
            "回答必须严格基于内部RAG知识库和Skills技能库，禁止使用外部通用知识。\n"
            "如果知识库中没有相关信息，明确告知用户'该问题暂无内部文档覆盖，请联系DBA团队'。\n"
            "回答必须包含以下结构：\n"
            "1. 排查思路\n"
            "2. 实用技巧\n"
            "3. 参数推荐\n"
            "4. 解决方案\n"
            "5. 风险避坑"
        )

    def search(self, query, category=None):
        # 自研数据库增强搜索
        results = super().search(query, category)
        return [r for r in results if r.confidence >= 0.25]


skill_registry.register(SelfDBSkill())
