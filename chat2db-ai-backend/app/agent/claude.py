"""
Claude Agent (Anthropic)
专用于自研数据库的深度推理
"""

import json
from typing import AsyncGenerator, Dict, List

import httpx

from app.config import settings
from app.core.logger import logger
from app.agent.base import BaseAgent


class ClaudeAgent(BaseAgent):
    name = "claude"
    provider = "anthropic"

    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL or "claude-opus-4-7"
        self.base_url = settings.CLAUDE_BASE_URL or "https://api.anthropic.com/v1"
        self.timeout = settings.agents_config.get("claude", {}).get("timeout", 90)

    def _convert_messages(self, messages: List[Dict[str, str]]) -> Dict:
        """将OpenAI格式消息转换为Anthropic格式"""
        system = ""
        conversation = []
        for m in messages:
            if m.get("role") == "system":
                system += m.get("content", "") + "\n"
            else:
                conversation.append({
                    "role": "user" if m.get("role") == "user" else "assistant",
                    "content": m.get("content", "")
                })
        return {"system": system.strip(), "messages": conversation}

    async def chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> str:
        converted = self._convert_messages(messages)
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "system": converted["system"],
            "messages": converted["messages"],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

    async def chat_stream(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        converted = self._convert_messages(messages)
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "system": converted["system"],
            "messages": converted["messages"],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:].strip()
                        try:
                            data = json.loads(chunk)
                            if data.get("type") == "content_block_delta":
                                text = data["delta"].get("text", "")
                                if text:
                                    yield text
                        except Exception:
                            continue
