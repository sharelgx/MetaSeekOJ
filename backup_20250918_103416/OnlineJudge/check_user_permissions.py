#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User
from problem.models import Problem

print("=== 检查用户权限 ===")
try:
    # 检查root用户的权限
    user = User.objects.get(username='root')
    print(f"用户名: {user.username}")
    print(f"Admin Type: {user.admin_type}")
    print(f"Problem Permission: {user.problem_permission}")
    print(f"Is Super Admin: {user.is_admin()}")
    
    # 检查是否可以管理所有题目
    if hasattr(user, 'can_mgmt_all_problem'):
        print(f"Can manage all problems: {user.can_mgmt_all_problem()}")
    else:
        print("can_mgmt_all_problem方法不存在")
    
    # 确保权限正确
    if user.problem_permission != 'ALL':
        print(f"\n⚠️  权限不正确，当前为: {user.problem_permission}")
        user.problem_permission = 'ALL'
        user.save()
        print("✅ 已更新problem_permission为ALL")
    else:
        print("✅ 权限配置正确")
        
except User.DoesNotExist:
    print("❌ root用户不存在")
except Exception as e:
    print(f"❌ 检查权限时出错: {e}")

print("\n=== 检查题目259状态 ===")
try:
    problem = Problem.objects.filter(id=259).first()
    if problem:
        print(f"题目ID: {problem.id}")
        print(f"题目标题: {problem.title}")
        print(f"当前visible状态: {problem.visible}")
        print(f"创建者: {problem.created_by.username}")
        print(f"是否为比赛题目: {problem.contest_id is not None}")
    else:
        print("❌ 题目259不存在")
except Exception as e:
    print(f"❌ 检查题目时出错: {e}")

print("\n=== 列出前5个题目状态 ===")
try:
    for p in Problem.objects.all()[:5]:
        print(f"ID: {p.id}, Title: {p.title[:30]}, Visible: {p.visible}, Creator: {p.created_by.username}")
except Exception as e:
    print(f"❌ 列出题目时出错: {e}")