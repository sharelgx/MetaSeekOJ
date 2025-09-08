#!/bin/bash

# MetaSeekOJ 项目快速重启脚本

echo "=== MetaSeekOJ 项目重启 ==="

# 停止现有服务
echo "停止现有服务..."
pkill -f "manage.py runserver" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "node.*8080" 2>/dev/null
pkill -f "redis-server" 2>/dev/null

# 等待进程停止
sleep 3

# 启动Redis服务
echo "启动Redis服务..."
nohup redis-server > /tmp/redis.log 2>&1 &
REDIS_PID=$!
echo "Redis服务已启动 (PID: $REDIS_PID)"

# 等待Redis启动
sleep 2

# 启动后端服务
echo "启动后端服务..."
cd /home/metaspeekoj/OnlineJudge
# 激活虚拟环境并启动Django服务
nohup bash -c "source venv/bin/activate && python manage.py runserver 0.0.0.0:8086" > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 5

# 启动前端服务
echo "启动前端服务..."
cd /home/metaspeekoj/OnlineJudgeFE
export NODE_OPTIONS="--openssl-legacy-provider"
nohup npm run dev -- --port 8080 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
sleep 5

# 检查服务状态
echo "检查服务状态..."
if netstat -tuln | grep -q ":6379 "; then
    echo "✓ Redis服务 (端口6379): 运行中"
else
    echo "✗ Redis服务 (端口6379): 未运行"
fi

if netstat -tuln | grep -q ":8086 "; then
    echo "✓ 后端服务 (端口8086): 运行中"
else
    echo "✗ 后端服务 (端口8086): 未运行"
fi

if netstat -tuln | grep -q ":8080 "; then
    echo "✓ 前端服务 (端口8080): 运行中"
else
    echo "✗ 前端服务 (端口8080): 未运行"
fi

echo ""
echo "=== 重启完成 ==="
echo "前端访问地址: http://localhost:8080"
echo "后端API地址: http://localhost:8086"
echo "查看日志: tail -f /tmp/redis.log 或 tail -f /tmp/backend.log 或 tail -f /tmp/frontend.log"