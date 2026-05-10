#!/bin/bash
# Chat2DB-AI 前端启动脚本

echo "🎨 Chat2DB-AI 前端启动中..."

if [ ! -d "node_modules" ]; then
    echo "📥 安装依赖..."
    npm install
fi

echo "🚀 启动开发服务器..."
npm run dev
