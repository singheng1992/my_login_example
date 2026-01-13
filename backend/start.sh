#!/bin/bash

echo "Starting Login Demo Backend..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
fi

# 创建上传目录
mkdir -p static/uploads/avatars

# 运行数据库迁移
echo "Running database migrations..."
alembic upgrade head

# 启动服务器
echo "Starting server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
