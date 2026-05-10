"""
MCP 统一调度引擎
整合 Model + Context + Prompt 三层，提供统一调用入口
"""

from typing import Any, Dict, List, Optional

from app.mcp.model import ContextWindowManager, ModelSelector
from app.mcp.context import ContextBuilder
from app.mcp.prompt import PromptEngine


class MCPEngine:
    """MCP调度引擎（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.selector = ModelSelector()
        self.context_manager = ContextWindowManager()
        self.builder = ContextBuilder()
        self.prompt_engine = PromptEngine()
        self._initialized = True

    def prepare(
        self,
        db_type: str,
        query: str,
        skill_results: List[Any] = None,
        rag_results: List[Any] = None,
        history: List[Dict[str, str]] = None,
    ) -> Dict:
        """
        准备完整的对话上下文和元信息

        Returns:
            {
                "messages": [...],
                "intent": "troubleshoot",
                "model_type": ModelType,
                "enhanced_query": "..."
            }
        """
        enhanced_query, intent = self.prompt_engine.analyze(query)

        messages = self.builder.build(
            db_type=db_type,
            query=enhanced_query,
            skill_results=skill_results,
            rag_results=rag_results,
            history=history,
        )
        messages = self.context_manager.trim(messages)

        model_type = self.selector.select(db_type)

        return {
            "messages": messages,
            "intent": intent,
            "model_type": model_type,
            "enhanced_query": enhanced_query,
        }

    def format(self, raw_answer: str, intent: str, sources: List[str] = None, model_used: str = None) -> Dict:
        """格式化模型输出为标准响应结构"""
        return self.prompt_engine.format_answer(raw_answer, intent, sources, model_used)


# 全局引擎
mcp_engine = MCPEngine()
