#!/usr/bin/env python
import os
import sys
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.import_serializers import ChoiceQuestionImportSerializer
from choice_question.models import ChoiceQuestion
from django.contrib.auth import get_user_model

User = get_user_model()

def test_import():
    # 读取测试文件
    test_file = '/home/metaspeekoj/TestCode/二级样题_标准模板.json'
    with open(test_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    # 测试所有题目
    test_questions = questions_data
    
    print(f"测试导入 {len(test_questions)} 道题目")
    
    # 获取或创建用户
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    
    # 准备导入数据
    import_data = {
        'questions': test_questions
    }
    
    # 执行导入
    serializer = ChoiceQuestionImportSerializer(data=import_data)
    if serializer.is_valid():
        result = serializer.save(created_by=user)
        print(f"导入成功: {result['success_count']}/{result['total_count']}")
        
        if result['errors']:
            print("导入错误:")
            for error in result['errors']:
                print(f"  题目 {error['index']}: {error['errors']}")
        
        # 检查导入的题目答案
        print("\n检查导入的题目答案:")
        for i, created_question in enumerate(result['created_questions']):
            original_correct = test_questions[i]['correct']
            imported_correct = created_question.correct_answer
            print(f"题目 {i+1}: 原始答案={original_correct}, 导入答案={imported_correct}, 匹配={'✓' if original_correct == imported_correct else '✗'}")
            
            # 显示选项详情
            options = json.loads(created_question.options) if isinstance(created_question.options, str) else created_question.options
            print(f"  选项: {[opt['key'] + ': ' + opt['text'][:20] + '...' for opt in options]}")
    else:
        print("导入验证失败:")
        print(serializer.errors)

if __name__ == '__main__':
    test_import()
