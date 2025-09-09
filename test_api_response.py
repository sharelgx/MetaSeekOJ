#!/usr/bin/env python3
"""
测试选择题API响应格式
验证options字段是否正确返回数组格式
"""

import requests
import json

def login_and_get_cookies():
    """登录并获取认证cookies"""
    login_url = "http://localhost:8086/api/login"
    login_data = {
        "username": "root",
        "password": "rootroot"
    }
    
    session = requests.Session()
    response = session.post(login_url, json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('error') is None:
            print("✅ 登录成功")
            return session
        else:
            print(f"❌ 登录失败: {result.get('data')}")
            return None
    else:
        print(f"❌ 登录请求失败: {response.status_code}")
        return None

def test_choice_question_api():
    """测试选择题详情API"""
    
    # 先登录
    session = login_and_get_cookies()
    if not session:
        print("无法登录，测试终止")
        return
    
    # 获取最新的题目ID
    print("\n=== 获取题目列表 ===")
    list_url = "http://localhost:8086/api/admin/choice_question"
    
    try:
        response = session.get(list_url)
        print(f"列表API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API响应结构: {type(data)}")
            print(f"API响应内容: {data}")
            
            # 处理不同的响应格式
            questions_data = None
            if isinstance(data, dict):
                if 'data' in data:
                    questions_data = data['data']
                elif 'results' in data:
                    questions_data = data['results']
                else:
                    questions_data = data
            elif isinstance(data, list):
                questions_data = data
            
            if questions_data and len(questions_data) > 0:
                # 获取最新的题目ID
                latest_question = questions_data[0]
                question_id = latest_question['id']
                print(f"最新题目ID: {question_id}")
                print(f"题目标题: {latest_question.get('title', 'N/A')}")
                
                # 测试详情API
                print(f"\n=== 测试题目详情API (ID: {question_id}) ===")
                detail_url = f"http://localhost:8086/api/admin/choice_question?id={question_id}"
                
                detail_response = session.get(detail_url)
                print(f"详情API状态码: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    question_data = detail_data.get('data', {})
                    
                    print(f"题目标题: {question_data.get('title', 'N/A')}")
                    print(f"题目类型: {question_data.get('question_type', 'N/A')}")
                    
                    # 重点检查options字段
                    options = question_data.get('options')
                    print(f"\n=== Options字段分析 ===")
                    print(f"Options类型: {type(options)}")
                    print(f"Options值: {options}")
                    
                    if isinstance(options, list):
                        print("✅ Options是数组格式 - 正确!")
                        print(f"选项数量: {len(options)}")
                        for i, option in enumerate(options):
                            print(f"  选项{i+1}: {option} (类型: {type(option)})")
                    elif isinstance(options, str):
                        print("❌ Options是字符串格式 - 需要修复!")
                        try:
                            parsed = json.loads(options)
                            print(f"解析后的选项: {parsed}")
                        except:
                            print("无法解析选项字符串")
                    else:
                        print(f"❓ Options是其他格式: {type(options)}")
                    
                    # 检查正确答案
                    correct_answer = question_data.get('correct_answer')
                    print(f"\n正确答案: {correct_answer} (类型: {type(correct_answer)})")
                    
                else:
                    print(f"详情API请求失败: {detail_response.text}")
            else:
                print("没有找到题目数据")
        else:
            print(f"列表API请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    test_choice_question_api()