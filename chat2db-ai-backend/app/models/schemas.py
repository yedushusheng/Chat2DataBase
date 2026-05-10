"""
Pydantic 数据模型定义
兼容 Chat2DB 接口规范
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话请求"""
    db_type: str = Field(default="mysql", description="数据库类型")
    query: str = Field(..., description="用户问题", min_length=1, max_length=4000)
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="历史对话")
    stream: bool = Field(default=False, description="是否流式返回")
    session_id: Optional[str] = Field(default=None, description="会话ID")


class ChatResponse(BaseModel):
    """对话响应（结构化答案）"""
    type: str = Field(default="general", description="意图类型")
    sections: List[Dict[str, str]] = Field(default=[], description="结构化段落")
    sources: List[str] = Field(default=[], description="知识来源")
    suggestion: str = Field(default="", description="后续建议")
    model_used: Optional[str] = Field(default=None, description="使用的模型")


class UploadResponse(BaseModel):
    """上传响应"""
    filename: str
    db_type: str
    chunks: int
    size: int


class FAQItem(BaseModel):
    """FAQ条目"""
    id: Optional[str] = None
    title: str
    category: Optional[str] = None
    db_type: Optional[str] = None
    confidence: Optional[float] = None


class DatabaseInfo(BaseModel):
    """数据库信息"""
    key: str
    name: str
    icon: str
    is_self: bool
    description: str
    color: Optional[str] = None
