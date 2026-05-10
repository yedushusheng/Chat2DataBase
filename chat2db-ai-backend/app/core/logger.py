"""
统一日志模块
支持 JSON / 文本 两种格式，集成 structlog
"""

import logging
import sys
from pathlib import Path

import structlog
from app.config import settings


def configure_logging():
    """初始化日志配置"""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.LOG_FORMAT == "json":
        formatter = structlog.dev.ConsoleRenderer(colors=False)
    else:
        formatter = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    # 文件日志
    if settings.get_yaml("logging.file.enabled", False):
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setLevel(level)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str):
    return structlog.get_logger(name)


logger = get_logger("chat2db")
