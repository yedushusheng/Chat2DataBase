"""
FastAPI 应用入口
兼容 Chat2DB 接口规范
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import chat_router
from app.api.database import db_router
from app.api.faq import faq_router
from app.api.upload import upload_router
from app.api.health import health_router
from app.config import settings
from app.core.exceptions import global_exception_handler
from app.core.logger import configure_logging, logger
from app.core.middleware import RequestContextMiddleware
from app.core.response import ResponseModel
from app.skills.registry import init_skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    configure_logging()
    init_skills()
    logger.info("app_starting", name=settings.APP_NAME, version=settings.APP_VERSION, env=settings.ENV)
    yield
    logger.info("app_stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级多数据库智能问答系统 - 对标 zoer.ai Pro",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 中间件
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(faq_router)
app.include_router(db_router)
app.include_router(health_router)


@app.get("/", response_model=ResponseModel)
async def root():
    return ResponseModel.success(
        data={"name": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs", "env": settings.ENV}
    )


@app.get("/api/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}
