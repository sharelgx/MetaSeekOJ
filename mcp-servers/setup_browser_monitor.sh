#!/bin/bash

# 浏览器日志监控工具安装脚本

echo "=== 浏览器日志监控工具安装 ==="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: pip3 未安装"
    exit 1
fi

echo "✓ pip3 已安装"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js 已安装: $(node --version)"

# 安装Python依赖
echo "安装Python依赖..."
pip3 install watchdog playwright requests

if [ $? -eq 0 ]; then
    echo "✓ Python依赖安装成功"
else
    echo "✗ Python依赖安装失败"
    exit 1
fi

# 安装Playwright浏览器
echo "安装Playwright浏览器..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo "✓ Playwright浏览器安装成功"
else
    echo "✗ Playwright浏览器安装失败"
    exit 1
fi

# 检查MCP playwright服务器
echo "检查MCP playwright服务器..."
npx -y @executeautomation/playwright-mcp-server --version 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ MCP playwright服务器可用"
else
    echo "⚠ MCP playwright服务器可能未正确配置"
fi

# 设置执行权限
chmod +x auto_browser_log_monitor.py
chmod +x mcp_browser_log_monitor.py

echo ""
echo "=== 安装完成 ==="
echo ""
echo "使用方法:"
echo "1. 基础版本: python3 auto_browser_log_monitor.py"
echo "2. MCP集成版本: python3 mcp_browser_log_monitor.py"
echo ""
echo "配置文件: browser_log_config.json"
echo "日志文件: browser_logs_*.json 和 browser_summary_*.txt"
echo ""
echo "启动前请确保:"
echo "- 前端开发服务器正在运行 (http://localhost:8080)"
echo "- 配置文件中的路径正确"
echo ""