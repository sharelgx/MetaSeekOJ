#!/usr/bin/env python3
import os
import django
import requests
import json
from urllib.parse import urljoin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

print("=== 模拟前端完整请求流程（包含CSRF处理） ===")

# 基础URL
BASE_URL = 'http://localhost:8000'

# 创建session保持cookie
session = requests.Session()

try:
    # 1. 首先访问首页获取CSRF cookie
    print("\n1. 访问首页获取CSRF cookie...")
    home_response = session.get(BASE_URL)
    print(f"首页响应状态码: {home_response.status_code}")
    
    # 检查是否获得了CSRF cookie
    csrf_cookie = None
    for cookie in session.cookies:
        if cookie.name == 'csrftoken':
            csrf_cookie = cookie.value
            print(f"✅ 获取到CSRF cookie: {csrf_cookie[:20]}...")
            break
    
    if not csrf_cookie:
        print("❌ 未获取到CSRF cookie")
        # 尝试直接访问API获取CSRF token
        print("尝试访问API获取CSRF token...")
        csrf_response = session.get(urljoin(BASE_URL, '/api/'))
        print(f"API响应状态码: {csrf_response.status_code}")
        for cookie in session.cookies:
            if cookie.name == 'csrftoken':
                csrf_cookie = cookie.value
                print(f"✅ 从API获取到CSRF cookie: {csrf_cookie[:20]}...")
                break
    
    # 2. 模拟前端登录流程
    print("\n2. 模拟前端登录...")
    login_url = urljoin(BASE_URL, '/api/login')
    login_data = {
        'username': 'root',
        'password': 'rootroot123'
    }
    
    # 设置CSRF header
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    if csrf_cookie:
        headers['X-CSRFToken'] = csrf_cookie
    
    login_response = session.post(login_url, json=login_data, headers=headers)
    print(f"登录响应状态码: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"登录响应: {login_result}")
        
        if login_result.get('error') != 'error':
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {login_result.get('data')}")
            exit(1)
    else:
        print(f"❌ 登录请求失败: {login_response.text}")
        exit(1)
    
    # 3. 获取题目信息
    print("\n3. 获取题目259信息...")
    get_problem_url = urljoin(BASE_URL, '/api/admin/problem')
    get_response = session.get(get_problem_url, params={'id': 259}, headers=headers)
    
    print(f"获取题目响应状态码: {get_response.status_code}")
    if get_response.status_code == 200:
        problem_data = get_response.json()
        if problem_data.get('error') is None:
            print("✅ 获取题目成功")
            problem_info = problem_data['data']
            print(f"题目标题: {problem_info['title']}")
            print(f"当前visible状态: {problem_info['visible']}")
            
            # 4. 模拟前端修改visible状态
            print("\n4. 模拟前端修改visible状态...")
            
            # 准备修改数据 - 完全模拟前端发送的数据结构
            edit_data = problem_info.copy()
            edit_data['visible'] = not edit_data['visible']  # 切换状态
            
            print(f"准备将visible从 {problem_info['visible']} 改为 {edit_data['visible']}")
            
            # 更新CSRF token（如果有新的）
            for cookie in session.cookies:
                if cookie.name == 'csrftoken':
                    headers['X-CSRFToken'] = cookie.value
                    break
            
            # 发送PUT请求
            put_url = urljoin(BASE_URL, '/api/admin/problem')
            put_response = session.put(
                put_url,
                json=edit_data,
                headers=headers
            )
            
            print(f"修改题目响应状态码: {put_response.status_code}")
            print(f"修改题目响应内容: {put_response.text}")
            
            if put_response.status_code == 200:
                put_result = put_response.json()
                if put_result.get('error') is None:
                    print("✅ 修改题目成功")
                    
                    # 5. 验证修改是否生效
                    print("\n5. 验证修改结果...")
                    verify_response = session.get(get_problem_url, params={'id': 259}, headers=headers)
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('error') is None:
                            new_visible = verify_data['data']['visible']
                            print(f"修改后visible状态: {new_visible}")
                            if new_visible == edit_data['visible']:
                                print("✅ 修改验证成功")
                            else:
                                print("❌ 修改未生效")
                        else:
                            print(f"❌ 验证请求失败: {verify_data}")
                    else:
                        print(f"❌ 验证请求失败: {verify_response.text}")
                else:
                    print(f"❌ 修改失败: {put_result}")
            else:
                print(f"❌ 修改请求失败: {put_response.text}")
                
        else:
            print(f"❌ 获取题目失败: {problem_data}")
    else:
        print(f"❌ 获取题目请求失败: {get_response.text}")
        
except Exception as e:
    print(f"❌ 测试过程中出错: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")