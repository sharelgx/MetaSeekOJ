#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.utils.validator import QuestionValidator
import json

def test_title_validation():
    print("测试标题验证...")
    
    # 加载测试数据
    with open('/home/metaspeekoj/TestCode/导入模板.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    validator = QuestionValidator()
    
    for i, item in enumerate(data, 1):
        title = item['question']
        print(f"\n第{i}个题目:")
        print(f"标题: {repr(title)}")
        
        errors = validator._validate_title(title)
        if errors:
            print(f"验证错误: {errors}")
        else:
            print("验证通过")
        
        # 检查是否包含<pre>标签
        has_pre = '<pre>' in title and '</pre>' in title
        print(f"包含<pre>标签: {has_pre}")

if __name__ == '__main__':
    test_title_validation()