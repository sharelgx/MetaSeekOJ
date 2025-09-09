#!/usr/bin/env python3
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
os.chdir('/home/metaspeekoj/OnlineJudge')
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
    
except User.DoesNotExist:
    print("错误: 未找到 root 用户!")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
