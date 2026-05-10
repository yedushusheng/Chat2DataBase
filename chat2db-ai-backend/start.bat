@echo off
chcp 65001 >nul
REM Chat2DB-AI 启动脚本 (Windows)

echo ========================================
echo Chat2DB-AI 企业级多数据库智能问答系统
echo ========================================
echo.

set ENV=%1
if "%ENV%"=="" set ENV=dev

set HOST=%2
if "%HOST%"=="" set HOST=0.0.0.0

set PORT=%3
if "%PORT%"=="" set PORT=8000

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 python，请先安装 Python 3.10+
    exit /b 1
)

REM 检查虚拟环境
if not exist venv (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -q -r requirements.txt

REM 创建必要目录
if not exist uploads mkdir uploads
if not exist chroma_db mkdir chroma_db
if not exist logs mkdir logs

echo.
echo 🚀 启动服务 [env=%ENV%, host=%HOST%, port=%PORT%]
echo.

python start.py --env %ENV% --host %HOST% --port %PORT%
