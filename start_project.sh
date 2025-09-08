#!/bin/bash

# MetaSeekOJ 项目快速启动脚本
# 使用方法: ./start_project.sh

echo "=== 启动 MetaSeekOJ 项目 ==="

# 使用Python重启脚本
python3 /home/metaspeekoj/mcp-servers/restart_project.py

echo ""
echo "项目启动完成！"
echo "前端访问: http://localhost:8080"
echo "后端API: http://localhost:8086"