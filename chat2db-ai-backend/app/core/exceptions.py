"""
全局异常定义与统一处理
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.core.response import ResponseModel


class Chat2DBException(Exception):
    """业务异常基类"""

    def __init__(self, code: int = 500, message: str = "服务器内部错误", detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(Chat2DBException):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(code=404, message="未找到", detail=detail)


class BadRequestException(Chat2DBException):
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(code=400, message="请求错误", detail=detail)


class UnauthorizedException(Chat2DBException):
    def __init__(self, detail: str = "未授权"):
        super().__init__(code=401, message="未授权", detail=detail)


class AgentException(Chat2DBException):
    def __init__(self, detail: str = "模型调用失败"):
        super().__init__(code=502, message="外部模型服务异常", detail=detail)


class RAGException(Chat2DBException):
    def __init__(self, detail: str = "知识库操作失败"):
        super().__init__(code=503, message="RAG服务异常", detail=detail)


class SQLCheckException(Chat2DBException):
    def __init__(self, detail: str = "SQL安全检查未通过"):
        super().__init__(code=400, message="SQL安全检查失败", detail=detail)


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    if isinstance(exc, Chat2DBException):
        logger.warning(
            "business_exception",
            path=request.url.path,
            code=exc.code,
            message=exc.message,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(code=exc.code, message=exc.message, data=exc.detail).model_dump(),
        )

    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.error(code=500, message="服务器内部错误", data=str(exc)).model_dump(),
    )
