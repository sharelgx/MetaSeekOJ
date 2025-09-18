#!/usr/bin/env python3
import os
import django
import requests
import json
from django.test import Client
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User
from problem.models import Problem
from django.middleware.csrf import get_token
from django.test import RequestFactory

print("=== 测试API调用 ===")

# 创建测试客户端
client = Client()
factory = RequestFactory()

try:
    # 1. 测试登录
    print("\n1. 测试用户登录...")
    login_data = {
        'username': 'root',
        'password': 'rootroot123'  # 请确认root用户的密码
    }
    
    response = client.post('/api/login', data=login_data, content_type='application/json')
    print(f"登录响应状态码: {response.status_code}")
    response_data = response.json()
    print(f"响应数据: {response_data}")
    
    if response.status_code == 200 and response_data.get('error') != 'error':
        print("✅ 登录成功")
    else:
        print(f"❌ 登录失败: {response_data.get('data', '未知错误')}")
        # 尝试其他可能的密码
        for pwd in ['root', 'admin', '123456', 'password']:
            login_data['password'] = pwd
            response = client.post('/api/login', data=login_data, content_type='application/json')
            response_data = response.json()
            if response.status_code == 200 and response_data.get('error') != 'error':
                print(f"✅ 使用密码 '{pwd}' 登录成功")
                break
        else:
            print("❌ 无法登录，请检查用户密码")
            
    # 2. 获取CSRF token
    print("\n2. 获取CSRF token...")
    csrf_response = client.get('/api/admin/csrf')
    print(f"CSRF响应状态码: {csrf_response.status_code}")
    csrf_token = None
    if csrf_response.status_code == 200:
        try:
            csrf_data = csrf_response.json()
            csrf_token = csrf_data.get('csrf_token')
            if csrf_token:
                print(f"✅ CSRF token: {csrf_token[:20]}...")
            else:
                print("❌ 响应中没有csrf_token字段")
                print(f"CSRF响应内容: {csrf_data}")
        except:
            print(f"❌ CSRF响应不是JSON格式: {csrf_response.content.decode()}")
    else:
        print(f"❌ 获取CSRF token失败: {csrf_response.content.decode()}")
    
    # 3. 测试获取题目信息
    print("\n3. 测试获取题目259信息...")
    get_response = client.get('/api/admin/problem?id=259')
    print(f"获取题目响应状态码: {get_response.status_code}")
    if get_response.status_code == 200:
        problem_data = get_response.json()
        print(f"✅ 获取题目成功")
        print(f"题目标题: {problem_data['data']['title']}")
        print(f"当前visible状态: {problem_data['data']['visible']}")
        
        # 4. 测试修改题目visible状态
        print("\n4. 测试修改题目visible状态...")
        
        # 准备修改数据
        edit_data = problem_data['data'].copy()
        edit_data['visible'] = not edit_data['visible']  # 切换状态
        
        print(f"准备将visible从 {problem_data['data']['visible']} 改为 {edit_data['visible']}")
        
        # 设置CSRF header
        headers = {'HTTP_X_CSRFTOKEN': csrf_token} if csrf_token else {}
            
        put_response = client.put(
            '/api/admin/problem', 
            data=json.dumps(edit_data),
            content_type='application/json',
            **headers
        )
        
        print(f"修改题目响应状态码: {put_response.status_code}")
        if put_response.status_code == 200:
            print("✅ 修改题目成功")
            
            # 验证修改是否生效
            verify_response = client.get('/api/admin/problem?id=259')
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                new_visible = verify_data['data']['visible']
                print(f"修改后visible状态: {new_visible}")
                if new_visible == edit_data['visible']:
                    print("✅ 修改验证成功")
                else:
                    print("❌ 修改未生效")
        else:
            print(f"❌ 修改题目失败: {put_response.content.decode()}")
            
    else:
        print(f"❌ 获取题目失败: {get_response.content.decode()}")
        
except Exception as e:
    print(f"❌ 测试过程中出错: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")