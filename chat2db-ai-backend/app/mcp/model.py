"""
MCP - Model 层
负责模型选择策略、上下文窗口管理、负载均衡
"""

import random
from enum import Enum
from typing import Dict, List, Optional

from app.config import settings
from app.core.logger import logger


class ModelType(str, Enum):
    """支持的模型类型"""
    DOUBAO = "doubao"
    WENXIN = "wenxin"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"
    SELF_RAG = "self_rag"


class ModelSelector:
    """模型选择器

    路由规则:
    - 自研数据库 -> CLAUDE (深度推理) 或 SELF_RAG (纯内部知识)
    - 非自研数据库 -> 按优先级选择外部Agent (DeepSeek / 豆包 / 文心 / GPT)
    """

    def __init__(self):
        self.priority = settings.EXTERNAL_MODEL_PRIORITY
        self.strategy = settings.ROUTER_STRATEGY
        self._round_robin_idx = 0
        self._fallback_enabled = settings.FALLBACK_ENABLED

    def select(self, db_type: str, prefer_stream: bool = False) -> ModelType:
        """根据数据库类型选择模型"""
        if self._is_self_db(db_type):
            # 自研数据库优先使用Claude深度推理
            logger.info("model_select_claude", db_type=db_type, reason="self_db")
            return ModelType.CLAUDE

        model_key = self._select_external()
        logger.info("model_select_external", db_type=db_type, model=model_key, strategy=self.strategy)
        return ModelType(model_key)

    def _is_self_db(self, db_type: str) -> bool:
        identifiers = [s.lower() for s in settings.SELF_DB_IDENTIFIERS]
        return db_type.lower() in identifiers or db_type.lower() == "self_db"

    def _select_external(self) -> str:
        if self.strategy == "priority":
            return self.priority[0] if self.priority else "deepseek"
        elif self.strategy == "round_robin":
            model = self.priority[self._round_robin_idx % len(self.priority)]
            self._round_robin_idx += 1
            return model
        else:
            return random.choice(self.priority)


class ContextWindowManager:
    """上下文窗口管理器 - 控制总token数不超过阈值"""

    def __init__(self, max_length: int = None):
        self.max_length = max_length or settings.mcp_config.get("max_context_length", 8000)

    def trim(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        total = 0
        trimmed = []
        system_msgs = [m for m in messages if m.get("role") == "system"]
        user_msgs = [m for m in messages if m.get("role") != "system"]

        for m in system_msgs:
            total += self._estimate_tokens(m.get("content", ""))
            trimmed.append(m)

        for m in reversed(user_msgs):
            cost = self._estimate_tokens(m.get("content", ""))
            if total + cost > self.max_length and len(trimmed) > len(system_msgs):
                break
            total += cost
            trimmed.insert(len(system_msgs), m)

        logger.debug("context_trimmed", original=len(messages), trimmed=len(trimmed), tokens=total)
        return trimmed

    def _estimate_tokens(self, text: str) -> int:
        chinese_chars = sum(1 for c in text if "一" <= c <= "鿿")
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + other_chars / 4)
