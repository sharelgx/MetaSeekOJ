#!/bin/bash

# MetaSeekOJ 优化启动脚本
# 支持SOLO模式和MCP模式

# 检查是否有参数
if [ "$1" == "--solo" ]; then
    echo "在SOLO模式下启动项目..."
    python3 /home/metaspeekoj/mcp-servers/optimized_restart.py --solo
    exit 0
fi

# 默认MCP模式
echo "在MCP模式下启动项目..."
python3 /home/metaspeekoj/mcp-servers/optimized_restart.py

echo "项目启动完成！"
echo "前端访问地址: http://localhost:8080"
echo "后端API地址: http://localhost:8086"