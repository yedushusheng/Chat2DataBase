#!/usr/bin/env python3
"""
Chat2DB-AI 启动脚本
支持开发/生产环境切换
"""

import argparse
import os
import sys
import uvicorn

# 强制 UTF-8 编码，避免 Windows 重定向日志时出现乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 使用国内 HuggingFace 镜像加速模型下载
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


def main():
    parser = argparse.ArgumentParser(description="Chat2DB-AI 启动脚本")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="运行环境")
    parser.add_argument("--host", default=None, help="绑定主机")
    parser.add_argument("--port", type=int, default=None, help="绑定端口")
    parser.add_argument("--workers", type=int, default=None, help="工作进程数")
    args = parser.parse_args()

    # 设置环境变量
    os.environ["ENV"] = "development" if args.env == "dev" else "production"

    # 动态加载配置
    from app.config import settings

    host = args.host or settings.HOST
    port = args.port or settings.PORT
    workers = args.workers or settings.WORKERS

    print("Chat2DB-AI 启动中...")
    print(f"   环境: {settings.ENV}")
    print(f"   地址: http://{host}:{port}")
    print(f"   文档: http://{host}:{port}/docs")
    print(f"   工作进程: {workers}")
    print("-" * 40)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=workers if settings.ENV == "production" else 1,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
