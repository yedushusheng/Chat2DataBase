#!/bin/bash
# Chat2DB-AI 启动脚本 (Linux/macOS)

set -e

ENV=${1:-dev}
HOST=${2:-0.0.0.0}
PORT=${3:-8000}

echo "================================"
echo "Chat2DB-AI 企业级多数据库智能问答系统"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 创建必要目录
mkdir -p uploads chroma_db logs skills_data

# 启动服务
echo ""
echo "🚀 启动服务 [env=$ENV, host=$HOST, port=$PORT]"
echo ""

python start.py --env $ENV --host $HOST --port $PORT
