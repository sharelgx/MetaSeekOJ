#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django
import requests
import json
import hashlib

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.models import Problem
from submission.models import Submission
from account.models import User
from utils.api import JSONResponse
from judge.dispatcher import JudgeDispatcher

def debug_judge_submission():
    print("=== 调试判题系统 ===")
    
    # 后端服务器配置
    backend_server_url = "http://localhost:8086"
    judge_server_token = "f977a4a1a2742839194c02f3e534f931c1ca13c4b3f303b1488e44703df0394c"
    
    print(f"使用后端服务器: {backend_server_url}")
    print(f"Token hash: {judge_server_token[:20]}...")
    
    # 获取一个题目
    problem = Problem.objects.first()
    if not problem:
        print("没有找到题目")
        return
    
    print(f"题目: {problem.title} (ID: {problem.id})")
    
    # 获取一个用户
    user = User.objects.first()
    if not user:
        print("没有找到用户")
        return
    
    print(f"用户: {user.username} (ID: {user.id})")
    
    # 准备提交数据
    submission_data = {
        "problem_id": problem.id,
        "language": "C++",
        "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
        # 移除contest_id和captcha字段，让API使用默认值
    }
    
    print(f"提交数据: {json.dumps(submission_data, indent=2)}")
    
    try:
        # 测试后端API连接
        print("\n=== 测试后端API连接 ===")
        api_url = f"{backend_server_url}/api/"
        print(f"API URL: {api_url}")
        api_response = requests.get(api_url, timeout=10)
        print(f"API响应状态码: {api_response.status_code}")
        
        # 创建会话并获取CSRF token
        print("\n=== 获取CSRF Token ===")
        session = requests.Session()
        
        # 访问用户profile API获取CSRF token (这个API有ensure_csrf_cookie装饰器)
        csrf_url = f"{backend_server_url}/api/profile/"
        csrf_response = session.get(csrf_url, timeout=10)
        print(f"CSRF响应状态码: {csrf_response.status_code}")
        
        # 从cookies中获取CSRF token
        csrf_token = session.cookies.get('csrftoken')
        print(f"CSRF Token: {csrf_token}")
        print(f"所有cookies: {dict(session.cookies)}")
        
        if not csrf_token:
            print("错误: 无法获取CSRF token")
            return
        
        # 用户登录
        print("\n=== 用户登录 ===")
        login_url = f"{backend_server_url}/api/login/"
        login_data = {
            "username": user.username,
            "password": "rootroot"  # 使用默认密码
        }
        
        login_headers = {
            'Content-Type': 'application/json',
            'X-Csrftoken': csrf_token if csrf_token else '',
            'Referer': backend_server_url
        }
        
        login_response = session.post(login_url, json=login_data, headers=login_headers, timeout=10)
        print(f"登录响应状态码: {login_response.status_code}")
        if login_response.status_code == 200:
            print(f"登录响应内容: {json.dumps(login_response.json(), indent=4, ensure_ascii=False)}")
            
            # 登录后重新获取CSRF token，因为Django会在登录后轮换token
            print("\n=== 登录后重新获取CSRF Token ===")
            csrf_response = session.get(f"{backend_server_url}/api/profile/", timeout=30)
            print(f"重新获取CSRF响应状态码: {csrf_response.status_code}")
            if csrf_response.status_code == 200:
                new_csrf_token = session.cookies.get('csrftoken')
                if new_csrf_token:
                    csrf_token = new_csrf_token
                    print(f"新的CSRF Token: {csrf_token}")
                else:
                    print("未能获取新的CSRF token")
        else:
            print(f"登录失败: {login_response.text}")
            return
        
        # 发送提交请求
        print("\n=== 发送提交请求 ===")
        submit_url = f"{backend_server_url}/api/submission/"
        print(f"提交URL: {submit_url}")
        
        # 使用form-data格式发送数据，包含CSRF token
        form_data = {
            'problem_id': submission_data['problem_id'],
            'language': submission_data['language'],
            'code': submission_data['code'],
            'csrfmiddlewaretoken': csrf_token
        }
        
        # 准备请求头
        headers = {
            'Referer': backend_server_url,
            'X-CSRFToken': csrf_token if csrf_token else ''
        }
        
        response = session.post(submit_url, data=form_data, headers=headers, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                result = response.json()
                print(f"提交结果: {json.dumps(result, indent=2)}")
                
                # 如果提交成功，检查提交状态
                if 'data' in result and 'submission_id' in result['data']:
                    submission_id = result['data']['submission_id']
                    print(f"\n=== 检查提交状态 ===")
                    print(f"提交ID: {submission_id}")
                    
                    # 查询数据库中的提交记录
                    try:
                        submission = Submission.objects.get(id=submission_id)
                        print(f"数据库中的提交状态: {submission.result}")
                        print(f"提交时间: {submission.create_time}")
                    except Submission.DoesNotExist:
                        print("在数据库中未找到提交记录")
                        
            except:
                print("响应不是JSON格式")
        else:
            print(f"提交失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_judge_submission()