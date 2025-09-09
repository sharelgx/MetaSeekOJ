#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试数据 - 包含字符串数组格式的选项
test_data = {
    "title": "测试试卷",
    "description": "用于测试选项导入功能的试卷",
    "questions": [
        {
            "title": "测试选择题",
            "content": "这是一道测试题",
            "question_type": "single",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "answer": "A",
            "score": 10
        }
    ]
}

def test_import():
    """测试试卷导入功能"""
    print("开始测试选项导入修复...")
    
    # 1. 登录获取token
    login_url = "http://localhost:8086/api/login"
    login_data = {
        "username": "root",
        "password": "rootroot"
    }
    
    print("1. 尝试登录...")
    try:
        login_response = requests.post(login_url, json=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        print(f"登录响应内容: {login_response.text}")
        
        if login_response.status_code != 200:
            print("登录失败，无法继续测试")
            return False
            
        login_result = login_response.json()
        if not login_result.get('error'):
            print(f"登录成功: {login_result}")
            # 使用session cookie而不是token
            session_cookies = login_response.cookies
            print(f"获取到cookies: {dict(session_cookies)}")
        else:
            print(f"登录失败: {login_result}")
            return False
            
    except Exception as e:
        print(f"登录请求异常: {e}")
        return False
    
    # 2. 调用导入API
    import_url = "http://localhost:8086/api/admin/exam_paper/import"
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\n2. 测试试卷导入...")
    try:
        import_response = requests.post(import_url, json=test_data, headers=headers, cookies=session_cookies)
        print(f"导入响应状态: {import_response.status_code}")
        print(f"导入响应内容: {import_response.text}")
        
        if import_response.status_code == 200:
            result = import_response.json()
            if not result.get('error'):
                print("✅ 导入成功！选项格式修复生效")
                return True
            else:
                print(f"❌ 导入失败: {result.get('data', '未知错误')}")
                return False
        else:
            print(f"❌ 导入请求失败，状态码: {import_response.status_code}")
            return False
            
    except Exception as e:
        print(f"导入请求异常: {e}")
        return False

if __name__ == "__main__":
    success = test_import()
    if success:
        print("\n🎉 测试通过！选项导入功能已修复")
    else:
        print("\n❌ 测试失败，需要进一步调试")