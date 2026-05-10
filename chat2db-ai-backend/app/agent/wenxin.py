"""
文心一言 (Baidu) Agent
使用 API Key + Secret Key 获取 Access Token
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List

import httpx

from app.config import settings
from app.core.logger import logger
from app.agent.base import BaseAgent


class WenxinAgent(BaseAgent):
    name = "wenxin"
    provider = "baidu"

    def __init__(self):
        self.api_key = settings.WENXIN_API_KEY
        self.secret_key = settings.WENXIN_SECRET_KEY
        self.model = settings.WENXIN_MODEL or "ernie-bot-4"
        self._access_token: str = ""
        self._token_lock = asyncio.Lock()
        self.timeout = settings.agents_config.get("wenxin", {}).get("timeout", 60)

    async def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        async with self._token_lock:
            if self._access_token:
                return self._access_token
            url = (
                f"https://aip.baidubce.com/oauth/2.0/token?"
                f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            )
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                self._access_token = data["access_token"]
                logger.info("wenxin_token_refreshed")
                return self._access_token

    async def chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> str:
        token = await self._get_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model}?access_token={token}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if "result" in data:
                return data["result"]
            raise RuntimeError(f"Wenxin error: {data}")

    async def chat_stream(
        self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        token = await self._get_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model}?access_token={token}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    line = line.strip()
                    if line.startswith("data: "):
                        chunk = line[6:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            text = data.get("result", "")
                            if text:
                                yield text
                        except Exception:
                            continue
