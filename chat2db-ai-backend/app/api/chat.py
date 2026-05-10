"""
对话接口
- POST /api/chat       非流式对话
- POST /api/chat/stream  SSE流式对话
- GET  /api/chat/history/{session_id}  获取会话历史
"""

from typing import List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.router import router as agent_router
from app.core.logger import logger
from app.core.response import ResponseModel
from app.models.schemas import ChatRequest

chat_router = APIRouter(prefix="/api/chat", tags=["对话"])


@chat_router.post("", response_model=ResponseModel)
async def chat(req: ChatRequest):
    """非流式对话接口"""
    logger.info("chat_request", db_type=req.db_type, query=req.query[:50], session=req.session_id)
    result = await agent_router.chat(
        db_type=req.db_type,
        query=req.query,
        history=req.history or [],
        use_stream=False,
    )
    return ResponseModel.success(data=result)


@chat_router.post("/stream")
async def chat_stream(req: ChatRequest):
    """SSE流式对话接口"""
    logger.info("chat_stream_request", db_type=req.db_type, query=req.query[:50], session=req.session_id)

    async def event_generator():
        try:
            async for chunk in agent_router.chat_stream(
                db_type=req.db_type,
                query=req.query,
                history=req.history or [],
            ):
                if chunk == "[DONE]":
                    yield "data: [DONE]\n\n"
                elif chunk.startswith("[错误]") or chunk.startswith("\n[错误]"):
                    for line in chunk.split("\n"):
                        yield f"data: {line}\n"
                    yield "\n"
                else:
                    for line in chunk.split("\n"):
                        yield f"data: {line}\n"
                    yield "\n"
        except Exception as e:
            logger.error("stream_error", error=str(e))
            for line in f"[ERROR] {str(e)}".split("\n"):
                yield f"data: {line}\n"
            yield "\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
