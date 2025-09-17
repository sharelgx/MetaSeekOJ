#!/usr/bin/env python3
import requests
import json

def test_choice_question_import():
    """测试选择题导入接口"""
    url = "http://localhost:8080/admin/choice-question/import"
    
    # 准备文件和数据
    with open('/home/metaspeekoj/TestCode/二级样题_标准模板.json', 'rb') as f:
        files = {'file': f}
        data = {'category_name': '测试分类'}
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"Choice Question Import Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success Count: {result.get('success_count', 0)}")
                print(f"Error Count: {result.get('error_count', 0)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Exception occurred: {e}")
            return False

def test_exam_paper_import():
    """测试试卷导入接口"""
    url = "http://localhost:8080/admin/exam-paper/import"
    
    # 准备文件和数据
    with open('/home/metaspeekoj/TestCode/二级样题_标准模板.json', 'rb') as f:
        files = {'file': f}
        data = {
            'category_name': '测试分类',
            'paper_title': '测试试卷',
            'language': 'C++'
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"\nExam Paper Import Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Paper ID: {result.get('paper_id', 'N/A')}")
                print(f"Success Count: {result.get('success_count', 0)}")
                print(f"Error Count: {result.get('error_count', 0)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Exception occurred: {e}")
            return False

def verify_answers():
    """验证导入的题目答案是否正确"""
    try:
        # 获取最近导入的题目
        response = requests.get("http://localhost:8080/api/choice-questions/?limit=20&ordering=-id")
        if response.status_code == 200:
            questions = response.json().get('results', [])
            print(f"\n=== 验证答案正确性 ===")
            print(f"找到 {len(questions)} 道题目")
            
            # 检查前几道题的答案
            for i, question in enumerate(questions[:5]):
                print(f"题目 {i+1}: {question.get('title', 'N/A')[:50]}...")
                print(f"  正确答案: {question.get('correct_answer', 'N/A')}")
                
                # 解析选项
                options = question.get('options', [])
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except:
                        pass
                        
                if options:
                    print(f"  选项数量: {len(options)}")
                    for j, option in enumerate(options[:4]):
                        if isinstance(option, dict):
                            print(f"    {chr(65+j)}: {option.get('text', 'N/A')[:30]}...")
                        else:
                            print(f"    {chr(65+j)}: {str(option)[:30]}...")
                print()
                
        else:
            print(f"获取题目失败: {response.status_code}")
            
    except Exception as e:
        print(f"验证答案时出错: {e}")

if __name__ == "__main__":
    print("开始测试导入功能...")
    
    # 测试选择题导入
    choice_success = test_choice_question_import()
    
    # 测试试卷导入
    paper_success = test_exam_paper_import()
    
    # 验证答案
    verify_answers()
    
    print(f"\n=== 测试结果 ===")
    print(f"选择题导入: {'成功' if choice_success else '失败'}")
    print(f"试卷导入: {'成功' if paper_success else '失败'}")