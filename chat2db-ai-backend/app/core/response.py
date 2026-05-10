"""
统一返回格式
{
  "code": 0,
  "message": "success",
  "data": {...},
  "timestamp": 1715432100
}
"""

import time
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一API响应结构"""

    code: int = Field(0, description="业务状态码，0为成功")
    message: str = Field("success", description="状态描述")
    data: Optional[T] = Field(None, description="业务数据")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="响应时间戳")

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "ResponseModel":
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "error", data: Any = None) -> "ResponseModel":
        return cls(code=code, message=message, data=data)
