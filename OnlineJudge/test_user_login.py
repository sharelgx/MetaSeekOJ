#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
from django.test import Client
import json

def test_user_permissions():
    print("=== 用户权限检查 ===")
    
    # 检查root用户
    try:
        root_user = User.objects.get(username='root')
        print(f"Root用户信息:")
        print(f"  用户名: {root_user.username}")
        print(f"  问题权限: {root_user.problem_permission}")
        print(f"  管理员类型: {root_user.admin_type}")
        print(f"  是否激活: {root_user.is_active}")
        print(f"  是否超级用户: {root_user.is_superuser}")
        print(f"  是否管理员: {root_user.is_staff}")
    except User.DoesNotExist:
        print("Root用户不存在")
        return
    
    # 测试登录API
    print("\n=== 测试登录API ===")
    client = Client()
    
    # 尝试登录
    login_data = {
        'username': 'root',
        'password': 'rootpassword'  # 请根据实际密码修改
    }
    
    response = client.post('/api/login/', data=json.dumps(login_data), 
                          content_type='application/json')
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.content.decode()}")
    
    if response.status_code == 200:
        # 登录成功后测试profile接口
        print("\n=== 测试Profile API ===")
        profile_response = client.get('/api/profile/')
        print(f"Profile响应状态码: {profile_response.status_code}")
        print(f"Profile响应内容: {profile_response.content.decode()}")
    
    # 检查当前活跃会话
    print("\n=== 检查活跃会话 ===")
    sessions = Session.objects.all()
    print(f"当前活跃会话数: {sessions.count()}")
    
    for session in sessions[:5]:  # 只显示前5个
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(f"  会话用户: {user.username}, 过期时间: {session.expire_date}")
            except User.DoesNotExist:
                print(f"  无效用户ID: {user_id}")

if __name__ == '__main__':
    test_user_permissions()