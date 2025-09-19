#!/bin/bash
# 环境切换脚本
# 用于在生产环境和测试环境之间切换

case "$1" in
    "production")
        echo "切换到生产环境..."
        export OJ_ENV=production
        export OJ_DOCKER=false
        echo "生产环境已激活"
        echo "后端服务端口: 8000"
        echo "前端服务端口: 8080"
        ;;
    "docker")
        echo "切换到Docker环境..."
        export OJ_ENV=dev
        export OJ_DOCKER=true
        echo "Docker环境已激活"
        echo "后端服务端口: 8086"
        echo "前端服务端口: 8080"
        ;;
    "test")
        echo "切换到测试环境..."
        export OJ_ENV=test
        export OJ_DOCKER=false
        echo "测试环境已激活"
        echo "后端服务端口: 8087"
        echo "前端服务端口: 8081"
        ;;
    "status")
        echo "当前环境状态:"
        echo "OJ_ENV: ${OJ_ENV:-未设置}"
        echo "OJ_DOCKER: ${OJ_DOCKER:-未设置}"
        echo ""
        echo "运行中的服务:"
        ps aux | grep -E '(runserver|rundramatiq|npm run dev)' | grep -v grep
        ;;
    *)
        echo "使用方法: $0 {production|docker|test|status}"
        echo ""
        echo "环境说明:"
        echo "  production - 生产环境 (端口8000)"
        echo "  docker     - Docker环境 (端口8086)"
        echo "  test       - 测试环境 (端口8087)"
        echo "  status     - 查看当前状态"
        exit 1
        ;;
esac