"""
MCP - Context 层
负责构建对话上下文：系统提示、知识库检索结果、历史对话、SQL上下文
"""

from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.logger import logger
from app.skills.base import skill_registry


class ContextBuilder:
    """上下文构建器：将 Skills、RAG、历史对话组装成模型可用的上下文"""

    def __init__(self):
        self.registry = skill_registry

    def build(
        self,
        db_type: str,
        query: str,
        skill_results: List[Any] = None,
        rag_results: List[Any] = None,
        history: List[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        messages = []

        # 1. 系统提示
        system_prompt = self._build_system_prompt(db_type)
        messages.append({"role": "system", "content": system_prompt})

        # 2. 知识上下文（Skills + RAG）
        knowledge_text = self._build_knowledge_block(skill_results, rag_results)
        if knowledge_text:
            messages.append({"role": "system", "content": f"【内部知识库引用】\n{knowledge_text}"})

        # 3. 历史对话（最近3轮）
        if history:
            for h in history[-6:]:
                messages.append(h)

        # 4. 当前用户问题
        messages.append({"role": "user", "content": query})

        logger.info(
            "context_built",
            db_type=db_type,
            skills_count=len(skill_results or []),
            rag_count=len(rag_results or []),
            history_len=len(history or []),
        )
        return messages

    def _build_system_prompt(self, db_type: str) -> str:
        skill = self.registry.get(db_type)
        if skill:
            base = skill.get_system_prompt()
        else:
            base = (
                "你是一位资深数据库专家，熟悉多种数据库系统。"
                "请为用户提供清晰的排查思路、实用技巧、参数推荐和解决方案。"
            )

        constraints = (
            "\n\n【回答规范】\n"
            "1. 必须分点回答，结构清晰，使用Markdown格式\n"
            "2. 若引用知识库，请标注来源 [来源: Skills/RAG]\n"
            "3. 参数调整必须说明是否需要重启、影响范围及风险\n"
            "4. SQL命令必须说明执行环境和备份要求\n"
            "5. 禁止提供任何可能破坏数据的危险命令，除非明确标注备份要求和回滚方案\n"
            "6. 如涉及生产变更，必须给出变更窗口建议和灰度方案"
        )
        return base + constraints

    def _build_knowledge_block(
        self, skill_results: List[Any] = None, rag_results: List[Any] = None
    ) -> str:
        parts = []

        if skill_results:
            parts.append("=== Skills技能库 ===")
            for r in skill_results[:5]:
                parts.append(f"[{r.category}] {r.title}\n{r.content}")

        if rag_results:
            parts.append("=== RAG文档知识 ===")
            for idx, doc in enumerate(rag_results[:5], 1):
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                source = doc.metadata.get("source", "未知") if hasattr(doc, "metadata") else "未知"
                parts.append(f"[文档{idx} - {source}]\n{content[:600]}")

        return "\n\n".join(parts)
