#!/usr/bin/env python3
import requests
import json

# 创建session保持cookies
session = requests.Session()

# 1. 首先访问首页获取CSRF token
print("1. 获取CSRF token...")
response = session.get('http://localhost:8080/')
csrf_token = None
for cookie in session.cookies:
    if cookie.name == 'csrftoken':
        csrf_token = cookie.value
        break

print(f"CSRF Token: {csrf_token}")

# 2. 登录admin账户
print("\n2. 登录admin账户...")
login_data = {
    'username': 'root',
    'password': 'rootroot'
}

headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrf_token
}

response = session.post('http://localhost:8080/api/login', 
                       json=login_data, 
                       headers=headers)
print(f"登录响应: {response.status_code}")
print(f"登录结果: {response.json()}")

# 3. 获取用户profile确认登录状态
print("\n3. 获取用户profile...")
response = session.get('http://localhost:8080/api/profile')
if response.status_code == 200:
    profile = response.json()
    if profile['error'] is None:
        user = profile['data']['user']
        print(f"用户: {user['username']}, 权限: {user['admin_type']}")
    else:
        print(f"获取profile失败: {profile['data']}")
else:
    print(f"获取profile失败: {response.status_code}")

# 4. 获取题目259的信息
print("\n4. 获取题目259信息...")
response = session.get('http://localhost:8080/api/admin/problem?id=259')
if response.status_code == 200:
    problem_data = response.json()
    if problem_data['error'] is None:
        problem = problem_data['data']
        print(f"题目ID: {problem['id']}, 标题: {problem['title']}, 可见性: {problem['visible']}")
        
        # 5. 尝试修改visible状态
        print("\n5. 修改题目可见性...")
        # 修改visible状态
        problem['visible'] = not problem['visible']
        problem['_id'] = problem['id']  # API需要_id字段
        
        response = session.put('http://localhost:8080/api/admin/problem',
                              json=problem,
                              headers=headers)
        print(f"修改响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"修改结果: {result}")
        else:
            print(f"修改失败: {response.text}")
            
        # 6. 验证修改结果
        print("\n6. 验证修改结果...")
        response = session.get('http://localhost:8080/api/admin/problem?id=259')
        if response.status_code == 200:
            updated_problem = response.json()
            if updated_problem['error'] is None:
                print(f"修改后可见性: {updated_problem['data']['visible']}")
            else:
                print(f"验证失败: {updated_problem['data']}")
    else:
        print(f"获取题目失败: {problem_data['data']}")
else:
    print(f"获取题目失败: {response.status_code}")