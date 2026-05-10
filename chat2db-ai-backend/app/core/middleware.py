"""
全局中间件
- 请求ID追踪
- 耗时统计
- SQL安全拦截（可选）
"""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.logger import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.time()
        logger.info(
            "request_start",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        response = await call_next(request)

        latency = round((time.time() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{latency}ms"

        logger.info(
            "request_end",
            request_id=request_id,
            status=response.status_code,
            latency_ms=latency,
        )
        return response
