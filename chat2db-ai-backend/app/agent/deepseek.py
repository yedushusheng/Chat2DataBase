"""
DeepSeek Agent
支持同步对话和SSE流式输出
"""

import json
from typing import AsyncGenerator, Dict, List

import httpx

from app.config import settings
from app.core.logger import logger
from app.agent.base import BaseAgent


class DeepSeekAgent(BaseAgent):
    name = "deepseek"
    provider = "deepseek"

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL or "deepseek-chat"
        self.base_url = settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com/v1"
        self.timeout = settings.agents_config.get("deepseek", {}).get("timeout", 60)

    async def chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
