#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ChoiceQuestion, Category

def assign_questions():
    print("=== 分配题目到测试分类 ===")
    
    # 获取测试分类
    cat = Category.objects.get(name='测试分类')
    
    # 分配2个简单题
    easy_questions = ChoiceQuestion.objects.filter(category__isnull=True, difficulty='easy')[:2]
    for q in easy_questions:
        q.category = cat
        q.save()
        print(f'将简单题 "{q.title}" 分配到测试分类')
    
    # 分配2个中等题
    medium_questions = ChoiceQuestion.objects.filter(category__isnull=True, difficulty='medium')[:2]
    for q in medium_questions:
        q.category = cat
        q.save()
        print(f'将中等题 "{q.title}" 分配到测试分类')
    
    # 检查结果
    test_cat_questions = ChoiceQuestion.objects.filter(category=cat)
    print(f"\n测试分类现在有 {test_cat_questions.count()} 个题目")
    
    # 按难度统计
    for difficulty in ['easy', 'medium', 'hard']:
        count = test_cat_questions.filter(difficulty=difficulty).count()
        print(f"  {difficulty}: {count}题")

if __name__ == '__main__':
    assign_questions()