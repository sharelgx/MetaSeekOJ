#!/usr/bin/env python3
"""
测试前端选择题页面显示
验证选项数据是否正确显示
"""

import requests
import json
import time

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

def test_choice_question_display():
    """测试选择题显示"""
    
    # 先登录
    session = login_and_get_cookies()
    if not session:
        print("无法登录，测试终止")
        return
    
    # 获取最新的题目ID
    print("\n=== 获取最新题目 ===")
    list_url = "http://localhost:8086/api/admin/choice_question"
    
    try:
        response = session.get(list_url)
        if response.status_code == 200:
            data = response.json()
            questions_data = data.get('data', [])
            
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
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    question_data = detail_data.get('data', {})
                    
                    print(f"题目标题: {question_data.get('title', 'N/A')}")
                    print(f"题目类型: {question_data.get('question_type', 'N/A')}")
                    
                    # 检查options字段
                    options = question_data.get('options')
                    print(f"\n=== 前端应该接收到的数据格式 ===")
                    print(f"Options类型: {type(options)}")
                    print(f"Options内容: {json.dumps(options, ensure_ascii=False, indent=2)}")
                    
                    if isinstance(options, list) and len(options) > 0:
                        print("\n=== 前端处理逻辑验证 ===")
                        for i, option in enumerate(options):
                            if isinstance(option, dict) and 'key' in option and 'text' in option:
                                print(f"✅ 选项{i+1}: key='{option['key']}', text='{option['text']}' - 应该被正确处理")
                            else:
                                print(f"❓ 选项{i+1}: {option} - 格式可能有问题")
                    
                    # 检查正确答案
                    correct_answer = question_data.get('correct_answer')
                    print(f"\n正确答案: {correct_answer}")
                    
                    print("\n=== 建议测试步骤 ===")
                    print(f"1. 打开浏览器访问: http://localhost:8080")
                    print(f"2. 登录管理员账户 (root/rootroot)")
                    print(f"3. 进入选择题管理页面")
                    print(f"4. 编辑题目ID: {question_id}")
                    print(f"5. 检查选项是否正确显示: {[opt.get('text', str(opt)) for opt in options if isinstance(opt, dict)]}")
                    
                else:
                    print(f"详情API请求失败: {detail_response.text}")
            else:
                print("没有找到题目数据")
        else:
            print(f"列表API请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    test_choice_question_display()