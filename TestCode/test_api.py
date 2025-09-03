#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# API 基础URL
BASE_URL = 'http://localhost:8080'

def test_create_choice_question():
    """测试创建选择题API"""
    
    # 模拟前端发送的数据（包含之前出错的格式）
    test_data = {
        'title': '测试选择题 - API调用',
        'description': '这是通过API创建的测试题目',
        'question_type': 'single',  # 这个字段之前缺失
        'difficulty': 'Easy',       # 这个格式之前不被接受
        'options': [                # 这个格式之前出错
            {'key': 'A', 'text': '选项A - 正确答案'},
            {'key': 'B', 'text': '选项B'},
            {'key': 'C', 'text': '选项C'},
            {'key': 'D', 'text': '选项D'}
        ],
        'correct_answer': 'A',
        'explanation': '选项A是正确答案，因为...',
        'score': 10,
        'visible': True,
        'is_public': True
    }
    
    print("测试创建选择题API...")
    print(f"发送数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 发送POST请求
        response = requests.post(
            f'{BASE_URL}/api/admin/choice-question/',
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                # 注意：实际使用时需要添加认证头
                # 'Authorization': 'Bearer your-token-here'
            },
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ API调用成功！选择题创建成功")
            return True
        else:
            print("❌ API调用失败")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Django服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return False

def test_multiple_formats():
    """测试多种数据格式"""
    
    test_cases = [
        {
            'name': '标准格式',
            'data': {
                'title': '标准格式测试题',
                'description': '测试标准数据格式',
                'question_type': 'single',
                'difficulty': 'easy',
                'options': [
                    {'key': 'A', 'text': '选项A'},
                    {'key': 'B', 'text': '选项B'}
                ],
                'correct_answer': 'A',
                'score': 10,
                'visible': True,
                'is_public': True
            }
        },
        {
            'name': '大写难度格式',
            'data': {
                'title': '大写难度测试题',
                'description': '测试大写难度格式',
                'question_type': 'single',
                'difficulty': 'Medium',  # 大写格式
                'options': [
                    {'key': 'A', 'text': '选项A'},
                    {'key': 'B', 'text': '选项B'}
                ],
                'correct_answer': 'A',
                'score': 15,
                'visible': True,
                'is_public': True
            }
        },
        {
            'name': '缺少question_type',
            'data': {
                'title': '缺少类型测试题',
                'description': '测试默认question_type',
                # 'question_type': 'single',  # 故意省略
                'difficulty': 'hard',
                'options': [
                    {'key': 'A', 'text': '选项A'},
                    {'key': 'B', 'text': '选项B'}
                ],
                'correct_answer': 'A',
                'score': 20,
                'visible': True,
                'is_public': True
            }
        }
    ]
    
    print("\n" + "="*50)
    print("测试多种数据格式...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}: {test_case['name']} ---")
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/admin/choice-question/',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"状态码: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ 成功")
            else:
                print("❌ 失败")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == '__main__':
    print("开始测试选择题创建API...")
    
    # 基础测试
    success = test_create_choice_question()
    
    if success:
        # 如果基础测试成功，继续测试多种格式
        test_multiple_formats()
    
    print("\n" + "="*50)
    print("测试完成！")
    print("\n注意：如果出现认证错误，这是正常的，因为我们没有提供认证令牌。")
    print("重要的是验证我们的序列化器修复是否解决了字段验证问题。")