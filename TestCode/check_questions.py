#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ChoiceQuestion, Category

def check_questions():
    print("=== 检查所有题目分类 ===")
    
    questions = ChoiceQuestion.objects.all()
    print(f"总题目数: {questions.count()}")
    
    # 按分类统计
    categories = Category.objects.all()
    print("\n分类统计:")
    for cat in categories:
        count = ChoiceQuestion.objects.filter(category=cat).count()
        print(f"  {cat.name}: {count}题")
    
    # 无分类题目
    no_category = ChoiceQuestion.objects.filter(category__isnull=True).count()
    print(f"  无分类: {no_category}题")
    
    print("\n详细题目信息:")
    for q in questions:
        category_name = q.category.name if q.category else "无分类"
        print(f"ID:{q.id}, 标题:{q.title[:30]}, 分类:{category_name}, 难度:{q.difficulty}")

if __name__ == '__main__':
    check_questions()