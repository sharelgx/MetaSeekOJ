#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.utils.helpers import format_answer

def test_format_answer():
    print("测试format_answer函数...")
    
    # 测试字符串输入
    test_cases = [
        ('3', "字符串'3'"),
        ('[3]', "字符串'[3]'"),
        (3, "整数3"),
        ([3], "列表[3]"),
        ('0,1,2', "字符串'0,1,2'"),
    ]
    
    for test_input, description in test_cases:
        try:
            result = format_answer(test_input)
            print(f"✓ {description}: {test_input} -> {result}")
        except Exception as e:
            print(f"✗ {description}: {test_input} -> 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_format_answer()