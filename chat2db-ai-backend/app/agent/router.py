"""
多模型Agent路由模块
- 自研数据库 -> Claude 深度推理
- 通用数据库 -> DeepSeek/豆包/文心/GPT 负载均衡 + 故障降级
"""

from typing import AsyncGenerator, Dict, List, Optional

from app.config import settings
from app.core.exceptions import AgentException
from app.core.logger import logger
from app.mcp.engine import mcp_engine
from app.mcp.model import ModelType
from app.skills.base import skill_registry
from app.rag.chroma_store import get_chroma_store

from app.agent.base import BaseAgent
from app.agent.deepseek import DeepSeekAgent
from app.agent.doubao import DoubaoAgent
from app.agent.wenxin import WenxinAgent
from app.agent.openai import OpenAIAgent
from app.agent.claude import ClaudeAgent


class AgentRouter:
    """Agent路由中心"""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {
            ModelType.DEEPSEEK: DeepSeekAgent(),
            ModelType.DOUBAO: DoubaoAgent(),
            ModelType.WENXIN: WenxinAgent(),
            ModelType.OPENAI: OpenAIAgent(),
            ModelType.CLAUDE: ClaudeAgent(),
        }

    async def chat(
        self, db_type: str, query: str, history: List[Dict[str, str]] = None, use_stream: bool = False
    ) -> dict:
        """统一对话入口"""
        # 1. Skills 检索
        skill = skill_registry.get(db_type)
        skill_results = skill.search(query) if skill else []

        # 2. RAG 检索
        rag_results = []
        store = get_chroma_store()
        rag_results = store.search(query, db_type=db_type)

        # 3. MCP 准备上下文
        mcp_result = mcp_engine.prepare(
            db_type=db_type,
            query=query,
            skill_results=skill_results,
            rag_results=rag_results,
            history=history,
        )
        messages = mcp_result["messages"]
        intent = mcp_result["intent"]
        model_type = mcp_result["model_type"]

        # 4. 模型调用
        if model_type == ModelType.SELF_RAG:
            answer = self._self_db_answer(skill_results, rag_results)
            sources = self._collect_sources(skill_results, rag_results)
            return mcp_engine.format(answer, intent, sources=sources, model_used="self_rag")

        agent = self._agents.get(model_type)
        if not agent:
            raise AgentException(f"未配置的模型: {model_type}")

        try:
            raw_answer = await agent.chat(messages)
            sources = self._collect_sources(skill_results, rag_results)
            return mcp_engine.format(raw_answer, intent, sources=sources, model_used=agent.name)
        except Exception as e:
            logger.error("agent_chat_failed", model=model_type.value, error=str(e))
            if settings.FALLBACK_ENABLED:
                fallback = await self._fallback_chat(messages, model_type)
                if fallback:
                    sources = self._collect_sources(skill_results, rag_results)
                    return mcp_engine.format(fallback, intent, sources=sources, model_used="fallback")
            raise AgentException(f"所有模型调用失败，最后错误: {str(e)}")

    async def chat_stream(
        self, db_type: str, query: str, history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """流式对话入口"""
        skill = skill_registry.get(db_type)
        skill_results = skill.search(query) if skill else []

        store = get_chroma_store()
        rag_results = store.search(query, db_type=db_type)

        mcp_result = mcp_engine.prepare(
            db_type=db_type, query=query,
            skill_results=skill_results, rag_results=rag_results, history=history,
        )
        messages = mcp_result["messages"]
        intent = mcp_result["intent"]
        model_type = mcp_result["model_type"]

        if model_type == ModelType.SELF_RAG:
            answer = self._self_db_answer(skill_results, rag_results)
            for sentence in answer.split("。"):
                if sentence.strip():
                    yield sentence.strip() + "。"
            yield "[DONE]"
            return

        agent = self._agents.get(model_type)
        if not agent:
            yield f"[错误] 未配置的模型: {model_type.value}"
            yield "[DONE]"
            return

        try:
            async for chunk in agent.chat_stream(messages):
                yield chunk
            yield "[DONE]"
        except Exception as e:
            logger.error("agent_stream_failed", model=model_type.value, error=str(e))
            if settings.FALLBACK_ENABLED:
                yield "\n[模型服务异常，正在切换备用模型...]\n"
                fallback = await self._fallback_chat(messages, model_type)
                if fallback:
                    yield fallback
                else:
                    yield "\n所有模型均不可用，请稍后重试。"
            else:
                yield f"\n[错误] {str(e)}"
            yield "[DONE]"

    def _self_db_answer(self, skill_results, rag_results) -> str:
        parts = []
        if skill_results:
            parts.append("=== 内部技能库 ===")
            for r in skill_results:
                parts.append(f"【{r.category}】{r.title}\n{r.content}")
        if rag_results:
            parts.append("=== 内部文档 ===")
            for doc in rag_results:
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                source = doc.metadata.get("source", "内部文档") if hasattr(doc, "metadata") else "内部文档"
                parts.append(f"[{source}]\n{content}")
        if not parts:
            return "该问题暂无内部文档覆盖，请联系DBA团队获取支持。"
        return "\n\n".join(parts)

    def _collect_sources(self, skill_results, rag_results) -> List[str]:
        sources = [r.title for r in skill_results]
        sources += [d.metadata.get("source", "") for d in rag_results if hasattr(d, "metadata")]
        return list(set(filter(None, sources)))

    async def _fallback_chat(self, messages: List[Dict[str, str]], failed_model) -> Optional[str]:
        priority = settings.EXTERNAL_MODEL_PRIORITY
        for key in priority:
            model_type = ModelType(key)
            if model_type == failed_model or model_type == ModelType.SELF_RAG:
                continue
            agent = self._agents.get(model_type)
            if not agent:
                continue
            try:
                logger.info("fallback_try", model=key)
                return await agent.chat(messages)
            except Exception as e:
                logger.warning("fallback_failed", model=key, error=str(e))
                continue
        return None


router = AgentRouter()
