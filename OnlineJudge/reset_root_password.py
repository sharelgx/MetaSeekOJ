#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User

print("=== 重置root用户密码 ===")

try:
    # 获取root用户
    user = User.objects.get(username='root')
    print(f"找到用户: {user.username}")
    print(f"用户ID: {user.id}")
    print(f"管理员类型: {user.admin_type}")
    
    # 重置密码为 'rootroot123'
    new_password = 'rootroot123'
    user.set_password(new_password)
    user.save()
    
    print(f"✅ 已重置root用户密码为: {new_password}")
    
    # 验证密码设置
    if user.check_password(new_password):
        print("✅ 密码验证成功")
    else:
        print("❌ 密码验证失败")
        
except User.DoesNotExist:
    print("❌ root用户不存在")
    # 创建root用户
    print("正在创建root用户...")
    user = User.objects.create_superuser(
        username='root',
        email='root@example.com',
        password='rootroot123',
        admin_type='Super Admin',
        problem_permission='ALL'
    )
    print(f"✅ 已创建root用户，密码: rootroot123")
    
except Exception as e:
    print(f"❌ 操作失败: {e}")
    import traceback
    traceback.print_exc()