#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_import_and_check():
    """测试导入功能并检查正确答案"""
    
    # 登录获取cookies
    login_url = 'http://localhost:8086/api/login'
    login_data = {
        'username': 'root',
        'password': 'rootroot'
    }
    
    session = requests.Session()
    login_response = session.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    print("登录成功")
    
    # 读取测试数据
    with open('/home/metaspeekoj/TestCode/二级样题.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 重新导入试卷
    import_url = 'http://localhost:8086/api/admin/exam_paper/import/'
    import_data = {
        'title': '二级样题测试（修复后）',
        'description': '测试正确答案导入修复',
        'questions': test_data
    }
    
    print("开始导入试卷...")
    import_response = session.post(import_url, json=import_data)
    
    if import_response.status_code == 201:
        result = import_response.json()
        print(f"导入成功！试卷ID: {result['data']['id']}")
        paper_id = result['data']['id']
        
        # 获取导入的题目列表
        questions_url = f'http://localhost:8086/api/admin/choice_question/?page=1&page_size=10'
        questions_response = session.get(questions_url)
        
        if questions_response.status_code == 200:
            questions_data = questions_response.json()
            print(f"\n获取题目列表成功，状态码: {questions_response.status_code}")
            
            if 'data' in questions_data and 'results' in questions_data['data']:
                questions = questions_data['data']['results']
                print(f"找到 {len(questions)} 道题目")
                
                # 检查最新的几道题目
                for i, question in enumerate(questions[:3]):
                    print(f"\n=== 题目 {i+1} ===")
                    print(f"ID: {question.get('id')}")
                    print(f"标题: {question.get('title', '无标题')[:50]}...")
                    print(f"正确答案: {question.get('correct_answer', '未找到')}")
                    
                    # 获取题目详情
                    detail_url = f"http://localhost:8086/api/admin/choice_question/{question['id']}/"
                    detail_response = session.get(detail_url)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if 'data' in detail_data:
                            detail = detail_data['data']
                            print(f"详情中的正确答案: {detail.get('correct_answer', '未找到')}")
                            
                            # 检查选项
                            options = detail.get('options', [])
                            if isinstance(options, str):
                                try:
                                    options = json.loads(options)
                                except:
                                    pass
                            
                            print(f"选项数量: {len(options) if isinstance(options, list) else '解析失败'}")
                            if isinstance(options, list) and len(options) > 0:
                                print(f"第一个选项: {options[0]}")
                    else:
                        print(f"获取详情失败: {detail_response.status_code}")
            else:
                print("响应数据格式异常")
                print(f"响应内容: {questions_data}")
        else:
            print(f"获取题目列表失败: {questions_response.status_code}")
            print(f"响应内容: {questions_response.text[:500]}")
    else:
        print(f"导入失败: {import_response.status_code}")
        print(f"错误信息: {import_response.text}")

if __name__ == '__main__':
    test_import_and_check()