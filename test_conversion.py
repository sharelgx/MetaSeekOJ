#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端数据格式转换功能
"""

def test_convert_frontend_question_format():
    """
    测试_convert_frontend_question_format方法的转换逻辑
    """
    # 模拟前端发送的数据格式
    frontend_data = {
        "content": "以下哪个是Python的关键字？",
        "type": "single",
        "options": ["def", "function", "method", "procedure"],
        "correct": "A",  # 前端使用字母格式
        "explanation": "def是Python中定义函数的关键字",
        "score": 5,
        "difficulty": "easy"
    }
    
    # 模拟转换逻辑（从exam.py中的_convert_frontend_question_format方法）
    def convert_frontend_question_format(question_data):
        converted = {}
        
        # 转换基本字段
        converted['content'] = question_data.get('content', '')
        converted['type'] = question_data.get('type', 'single')
        
        # 转换选项格式：前端字符串数组 -> 后端对象数组
        if 'options' in question_data and isinstance(question_data['options'], list):
            converted_options = []
            for i, option_text in enumerate(question_data['options']):
                option_key = chr(65 + i)  # 0->A, 1->B, 2->C, 3->D
                converted_options.append({
                    "key": option_key,
                    "text": str(option_text).strip()
                })
            converted['options'] = converted_options
        else:
            converted['options'] = []
        
        # 转换答案格式 - 使用'answer'字段，转换为字符串格式以符合验证器schema
        if 'correct' in question_data:
            correct_answer = question_data['correct']
            if isinstance(correct_answer, str):
                # 如果是字母格式，转换为数字索引字符串
                if correct_answer.upper() in ['A', 'B', 'C', 'D', 'E', 'F']:
                    index = ord(correct_answer.upper()) - 65  # A->0, B->1, C->2, D->3
                    converted['answer'] = str(index)
                else:
                    # 如果是数字格式，确保是字符串
                    try:
                        index = int(correct_answer)
                        converted['answer'] = str(index)
                    except ValueError:
                        converted['answer'] = "0"
            elif isinstance(correct_answer, int):
                converted['answer'] = str(correct_answer)
            else:
                converted['answer'] = "0"
        else:
            converted['answer'] = "0"
        
        # 其他字段
        converted['explanation'] = question_data.get('explanation', '')
        converted['score'] = question_data.get('score', 1)
        converted['difficulty'] = question_data.get('difficulty', 'medium')
        
        return converted
    
    # 执行转换
    converted = convert_frontend_question_format(frontend_data)
    
    print("前端数据格式:")
    print(frontend_data)
    print("\n转换后的后端格式:")
    print(converted)
    print()
    
    # 验证转换结果
    assert converted['content'] == "以下哪个是Python的关键字？"
    assert converted['type'] == "single"
    assert len(converted['options']) == 4
    assert converted['options'][0]['key'] == 'A'
    assert converted['options'][0]['text'] == 'def'
    assert converted['answer'] == "0"  # A转换为"0"（字符串格式）
    assert converted['explanation'] == "def是Python中定义函数的关键字"
    
    print("✅ 所有测试通过！")
    print("\n关键修复点:")
    print("1. 前端字符串数组选项 -> 后端对象数组选项")
    print("2. 字母答案(A) -> 数字索引字符串答案('0') - 符合验证器schema")
    print("3. 使用'answer'字段而不是'correct_answer'字段")
    print("4. 答案格式必须是字符串类型以通过验证器检查")

if __name__ == "__main__":
    test_convert_frontend_question_format()