#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamPaper, ChoiceQuestion

def debug_question_generation():
    print("=== 调试题目生成逻辑 ===")
    
    # 获取试卷信息
    paper = ExamPaper.objects.get(id=7)
    print(f"试卷: {paper.title}")
    print(f"需要题目数: {paper.question_count}")
    print(f"难度分布: {paper.difficulty_distribution}")
    print(f"试卷分类: {list(paper.categories.values_list('name', flat=True))}")
    
    # 检查所有题目
    all_questions = ChoiceQuestion.objects.all()
    print(f"\n数据库中总题目数: {all_questions.count()}")
    
    # 检查visible字段
    visible_questions = ChoiceQuestion.objects.filter(visible=True)
    print(f"可见的题目数: {visible_questions.count()}")
    
    # 按分类筛选
    category_filtered = visible_questions.filter(category__in=paper.categories.all())
    print(f"分类筛选后题目数: {category_filtered.count()}")
    
    # 按难度统计
    print("\n各难度题目数量:")
    for difficulty in ['easy', 'medium', 'hard']:
        count = category_filtered.filter(difficulty=difficulty).count()
        print(f"  {difficulty}: {count}")
    
    # 模拟题目生成
    print("\n模拟题目生成:")
    questions = []
    difficulty_distribution = paper.difficulty_distribution or {}
    
    for difficulty, count in difficulty_distribution.items():
        if count > 0:
            difficulty_questions = category_filtered.filter(difficulty=difficulty)[:count]
            questions.extend(list(difficulty_questions))
            print(f"  {difficulty}难度需要{count}题，实际获得{len(difficulty_questions)}题")
    
    print(f"\n总共生成题目数: {len(questions)}")
    print(f"目标题目数: {paper.question_count}")
    
    if len(questions) < paper.question_count:
        print("题目不足，需要随机补充")
        remaining_count = paper.question_count - len(questions)
        remaining_questions = category_filtered.exclude(
            id__in=[q.id for q in questions]
        )[:remaining_count]
        print(f"可补充题目数: {remaining_questions.count()}")
        questions.extend(list(remaining_questions))
        print(f"补充后总题目数: {len(questions)}")
    
    return len(questions) >= paper.question_count

if __name__ == '__main__':
    success = debug_question_generation()
    print(f"\n题目生成{'成功' if success else '失败'}")