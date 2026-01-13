#!/bin/bash

echo "Starting Login Demo Frontend..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    exit 1
fi

# 启动HTTP服务器
echo "Starting server on http://localhost:8080"
cd $(dirname "$0")
python3 -m http.server 8080
