#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择题导入功能测试脚本
"""

import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import_format():
    """
    测试导入数据格式验证
    """
    print("=== 测试导入数据格式验证 ===")
    
    # 测试用例1：正确格式
    valid_data = {
        "questions": [
            {
                "question": "测试题目",
                "type": "single",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "correct": "A",
                "explanation": "测试解析"
            }
        ]
    }
    
    print("\n1. 测试正确格式:")
    print(json.dumps(valid_data, ensure_ascii=False, indent=2))
    
    # 测试用例2：缺少必填字段
    invalid_data1 = {
        "questions": [
            {
                "question": "测试题目",
                "options": ["选项A", "选项B"]
                # 缺少type和correct字段
            }
        ]
    }
    
    print("\n2. 测试缺少必填字段:")
    print(json.dumps(invalid_data1, ensure_ascii=False, indent=2))
    
    # 测试用例3：错误的答案格式
    invalid_data2 = {
        "questions": [
            {
                "question": "测试题目",
                "type": "single",
                "options": ["选项A", "选项B"],
                "correct": "C"  # 答案超出选项范围
            }
        ]
    }
    
    print("\n3. 测试错误的答案格式:")
    print(json.dumps(invalid_data2, ensure_ascii=False, indent=2))
    
    # 测试用例4：多选题格式
    multiple_data = {
        "questions": [
            {
                "question": "多选题测试",
                "type": "multiple",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "correct": "A,C",
                "explanation": "多选题解析"
            }
        ]
    }
    
    print("\n4. 测试多选题格式:")
    print(json.dumps(multiple_data, ensure_ascii=False, indent=2))

def validate_question_data(question_data):
    """
    验证单个题目数据
    """
    errors = []
    
    # 检查必填字段
    required_fields = ['question', 'type', 'options', 'correct']
    for field in required_fields:
        if field not in question_data:
            errors.append(f"缺少必填字段: {field}")
    
    if errors:
        return False, errors
    
    # 验证题目类型
    if question_data['type'] not in ['single', 'multiple']:
        errors.append(f"无效的题目类型: {question_data['type']}")
    
    # 验证选项
    options = question_data['options']
    if not isinstance(options, list) or len(options) < 2:
        errors.append("选项必须是列表且至少包含2个选项")
    
    # 验证正确答案
    correct = question_data['correct']
    if ',' in correct:
        correct_answers = [ans.strip().upper() for ans in correct.split(',')]
    else:
        correct_answers = [correct.strip().upper()]
    
    for answer in correct_answers:
        if not answer.isalpha() or len(answer) != 1:
            errors.append(f"答案格式错误: {answer}")
            continue
        
        answer_index = ord(answer) - ord('A')
        if answer_index >= len(options):
            errors.append(f"答案 {answer} 超出选项范围")
    
    # 验证单选题只能有一个答案
    if question_data['type'] == 'single' and len(correct_answers) > 1:
        errors.append("单选题只能有一个正确答案")
    
    return len(errors) == 0, errors

def test_validation():
    """
    测试验证逻辑
    """
    print("\n=== 测试验证逻辑 ===")
    
    test_cases = [
        {
            "name": "正确的单选题",
            "data": {
                "question": "测试题目",
                "type": "single",
                "options": ["选项A", "选项B", "选项C"],
                "correct": "A"
            }
        },
        {
            "name": "正确的多选题",
            "data": {
                "question": "测试题目",
                "type": "multiple",
                "options": ["选项A", "选项B", "选项C"],
                "correct": "A,C"
            }
        },
        {
            "name": "缺少必填字段",
            "data": {
                "question": "测试题目",
                "options": ["选项A", "选项B"]
            }
        },
        {
            "name": "答案超出范围",
            "data": {
                "question": "测试题目",
                "type": "single",
                "options": ["选项A", "选项B"],
                "correct": "C"
            }
        },
        {
            "name": "单选题多个答案",
            "data": {
                "question": "测试题目",
                "type": "single",
                "options": ["选项A", "选项B", "选项C"],
                "correct": "A,B"
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n测试用例: {case['name']}")
        is_valid, errors = validate_question_data(case['data'])
        if is_valid:
            print("✓ 验证通过")
        else:
            print("✗ 验证失败:")
            for error in errors:
                print(f"  - {error}")

if __name__ == "__main__":
    print("选择题导入功能测试")
    print("=" * 50)
    
    test_import_format()
    test_validation()
    
    print("\n=== 测试完成 ===")
    print("\n使用说明:")
    print("1. 确保导入数据包含questions数组")
    print("2. 每个题目必须包含: question, type, options, correct")
    print("3. type只能是'single'或'multiple'")
    print("4. options至少包含2个选项")
    print("5. correct格式为A-Z字母，多选用逗号分隔")
    print("6. 单选题只能有一个正确答案")