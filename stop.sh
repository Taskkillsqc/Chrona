#!/bin/bash

# Dummy Schedule Manager 停止脚本

echo "🛑 正在停止 Dummy Schedule Manager..."

# Docker 环境停止
if [ -f "docker-compose.yml" ]; then
    echo "🐳 检测到 Docker Compose 配置，停止容器..."
    docker-compose down
fi

# 查找并停止本地运行的进程
PIDS=$(pgrep -f "python.*agent.py" || true)

if [ -n "$PIDS" ]; then
    echo "🔍 发现运行中的进程: $PIDS"
    echo "📤 发送停止信号..."
    kill -TERM $PIDS
    
    # 等待进程优雅关闭
    sleep 5
    
    # 检查进程是否仍在运行
    REMAINING=$(pgrep -f "python.*agent.py" || true)
    if [ -n "$REMAINING" ]; then
        echo "⚠️  进程未响应优雅关闭，强制终止..."
        kill -KILL $REMAINING
    fi
    
    echo "✅ Dummy Schedule Manager 已停止"
else
    echo "ℹ️  未发现运行中的 Dummy Schedule Manager 进程"
fi

echo "👋 停止完成"
