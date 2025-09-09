#!/bin/bash

echo "🔧 开始修复管理员权限问题..."

# 停止现有服务
echo "停止现有服务..."
pkill -f "python manage.py runserver"
pkill -f "npm run dev"
sleep 2

# 1. 修复后端权限（在虚拟环境中）
echo "1. 修复后端用户权限..."
cd /home/metaspeekoj/OnlineJudge

# 激活虚拟环境并修复权限
source django_env/bin/activate
python3 << 'EOF'
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User, ProblemPermission, AdminType

try:
    # Get root user
    user = User.objects.get(username='root')
    
    print("=== 当前 root 用户状态 ===")
    print(f"用户名: {user.username}")
    print(f"admin_type: '{user.admin_type}' (类型: {type(user.admin_type)})")
    print(f"problem_permission: '{user.problem_permission}'")
    print(f"is_superuser: {user.is_superuser}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_active: {user.is_active}")
    
    print("\n=== 常量值对比 ===")
    print(f"AdminType.ADMIN: '{AdminType.ADMIN}'")
    print(f"AdminType.SUPER_ADMIN: '{AdminType.SUPER_ADMIN}'")
    print(f"ProblemPermission.ALL: '{ProblemPermission.ALL}'")
    
    print("\n=== 权限检查结果 ===")
    is_admin = user.admin_type == AdminType.ADMIN
    is_super_admin = user.admin_type == AdminType.SUPER_ADMIN
    has_admin_permission = is_admin or is_super_admin
    
    print(f"是否为 ADMIN: {is_admin}")
    print(f"是否为 SUPER_ADMIN: {is_super_admin}")
    print(f"是否有管理员权限: {has_admin_permission}")
    
    # 如果权限不正确，修复它
    if not has_admin_permission:
        print("\n=== 修复权限 ===")
        user.admin_type = AdminType.SUPER_ADMIN
        user.problem_permission = ProblemPermission.ALL
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("权限已修复!")
        
        # 重新验证
        user.refresh_from_db()
        print(f"修复后 admin_type: '{user.admin_type}'")
        print(f"修复后 problem_permission: '{user.problem_permission}'")
    else:
        print("\n✅ 权限已经正确设置")
    
except User.DoesNotExist:
    print("错误: 未找到 root 用户!")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
EOF

# 2. 启动 Django 后端（在虚拟环境中）
echo "2. 启动 Django 后端..."
nohup python manage.py runserver 0.0.0.0:8001 > /home/metaspeekoj/django.log 2>&1 &
DJANGO_PID=$!
sleep 3

# 3. 启动 Vue 前端
echo "3. 启动 Vue 前端..."
cd /home/metaspeekoj/OnlineJudgeFE
nohup npm run dev > /home/metaspeekoj/vue.log 2>&1 &
VUE_PID=$!
sleep 5

# 4. 测试服务状态
echo "4. 测试服务状态..."

# 测试后端
if curl -s http://localhost:8001/api/website/ >/dev/null; then
    echo "✅ Django 后端正常 (http://localhost:8001)"
else
    echo "❌ Django 后端启动失败"
    echo "Django 日志最后10行:"
    tail -10 /home/metaspeekoj/django.log
fi

# 测试前端
if curl -s http://localhost:8080/ >/dev/null; then
    echo "✅ Vue 前端正常 (http://localhost:8080)"
else
    echo "❌ Vue 前端启动失败"
    echo "Vue 日志最后10行:"
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
echo "📝 根据您提供的日志，权限验证已经通过，但如果仍有问题："
echo "   1. 请清除浏览器缓存后重试"
echo "   2. 按 F12 打开开发者工具查看是否有其他错误"
echo "   3. 尝试访问不同的管理页面"

echo ""
echo "🔄 服务控制:"
echo "停止服务: kill $DJANGO_PID $VUE_PID"

echo ""
echo "=== 修复完成 ==="
