#!/bin/bash

echo "🔧 开始修复管理员权限问题..."

# 1. 修复后端权限
echo "1. 修复后端用户权限..."
cd /home/metaspeekoj
python3 debug_admin_permissions.py

# 2. 重启服务
echo "2. 重启服务..."

# 停止现有服务
echo "停止现有服务..."
pkill -f "python manage.py runserver"
pkill -f "npm run dev"
sleep 2

# 切换到 Django 项目目录
cd /home/metaspeekoj/OnlineJudge

# 启动 Django 后端
echo "启动 Django 后端..."
nohup python manage.py runserver 0.0.0.0:8001 > /home/metaspeekoj/django.log 2>&1 &
DJANGO_PID=$!
sleep 3

# 切换到前端目录
cd /home/metaspeekoj/OnlineJudgeFE

# 启动 Vue 前端
echo "启动 Vue 前端..."
nohup npm run dev > /home/metaspeekoj/vue.log 2>&1 &
VUE_PID=$!
sleep 5

# 3. 测试服务状态
echo "3. 测试服务状态..."

# 测试后端
if curl -s http://localhost:8001/api/website/ >/dev/null; then
    echo "✅ Django 后端正常 (http://localhost:8001)"
else
    echo "❌ Django 后端启动失败"
    tail -10 /home/metaspeekoj/django.log
fi

# 测试前端
if curl -s http://localhost:8080/ >/dev/null; then
    echo "✅ Vue 前端正常 (http://localhost:8080)"
else
    echo "❌ Vue 前端启动失败"
    tail -10 /home/metaspeekoj/vue.log
fi

echo ""
echo "🎯 修复完成！现在请尝试："
echo "=================================="
echo "1. 访问管理界面: http://localhost:8080/admin/"
echo "2. 登录账号: root"
echo "3. 登录密码: rootroot"
echo "4. 访问专题管理: http://localhost:8080/admin/#/topic/management"
echo "=================================="

echo ""
echo "📝 如果仍有问题，请在浏览器开发者工具控制台查看详细日志"
echo "   或运行以下命令查看服务日志:"
echo "   Django日志: tail -f /home/metaspeekoj/django.log"
echo "   Vue日志: tail -f /home/metaspeekoj/vue.log"

echo ""
echo "🔄 服务控制:"
echo "停止服务: kill $DJANGO_PID $VUE_PID"

echo ""
echo "=== 修复完成 ==="
