"""
Agent基类与统一接口
所有外部模型Agent必须继承此类
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List


class BaseAgent(ABC):
    """外部模型Agent基类"""

    name: str = "base"
    provider: str = "base"

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """同步对话，返回完整文本"""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐字返回"""
        pass

    def health_check(self) -> bool:
        return True
