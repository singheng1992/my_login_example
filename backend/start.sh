#!/bin/bash

echo "Starting Login Demo Backend..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
fi

# 创建上传目录
mkdir -p static/uploads/avatars

# 同步依赖
echo "Syncing dependencies with uv..."
uv sync

# 运行数据库迁移
echo "Running database migrations..."
uv run alembic upgrade head

# 启动服务器
echo "Starting server on http://localhost:8000"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
