#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查选择题正确答案导入情况
"""

import requests
import json

def login_and_get_cookies():
    """登录并获取cookies"""
    login_url = "http://localhost:8086/api/login"
    login_data = {
        "username": "root",
        "password": "rootroot"
    }
    
    session = requests.Session()
    response = session.post(login_url, json=login_data)
    
    if response.status_code == 200:
        print("登录成功")
        return session
    else:
        print(f"登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return None

def check_choice_question_data(session):
    """检查选择题数据"""
    # 获取最新的选择题
    list_url = "http://localhost:8086/api/admin/choice_question/?page=1&page_size=10"
    response = session.get(list_url)
    
    print(f"题目列表API状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"API响应结构: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 尝试不同的数据结构
        questions = None
        if 'data' in data and 'results' in data['data'] and data['data']['results']:
            questions = data['data']['results']
        elif 'data' in data and isinstance(data['data'], list):
            questions = data['data']
        elif 'results' in data:
            questions = data['results']
        elif isinstance(data, list):
            questions = data
        
        if questions and len(questions) > 0:
            # 获取最新题目
            latest_question = questions[0]
            question_id = latest_question['id']
            print(f"最新题目ID: {question_id}")
            
            # 直接从列表数据中检查题目信息
            print("\n=== 题目数据检查 ===")
            print(json.dumps(latest_question, indent=2, ensure_ascii=False))
            
            # 重点检查正确答案相关字段
            print("\n=== 正确答案相关字段检查 ===")
            print(f"correct_answer: {latest_question.get('correct_answer', 'NOT FOUND')}")
            print(f"answer: {latest_question.get('answer', 'NOT FOUND')}")
            print(f"correct: {latest_question.get('correct', 'NOT FOUND')}")
            print(f"right_answer: {latest_question.get('right_answer', 'NOT FOUND')}")
            
            # 检查选项数据
            options = latest_question.get('options', [])
            print(f"\n选项数据类型: {type(options)}")
            print(f"选项数据内容: {options}")
            
            if isinstance(options, list) and options:
                print("\n=== 选项详细信息 ===")
                for i, option in enumerate(options):
                    print(f"选项 {i}: {option} (类型: {type(option)})")
                    if isinstance(option, dict):
                        print(f"  - key: {option.get('key', 'N/A')}")
                        print(f"  - text: {option.get('text', 'N/A')}")
        else:
            print("没有找到题目数据")
    else:
        print(f"获取题目列表失败: {response.text}")

def main():
    print("开始检查选择题正确答案导入情况...")
    
    # 登录
    session = login_and_get_cookies()
    if not session:
        return
    
    # 检查选择题数据
    check_choice_question_data(session)
    
    print("\n检查完成！")

if __name__ == "__main__":
    main()