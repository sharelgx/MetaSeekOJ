#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamPaper, Category

# 模拟API中的查询逻辑
print('=== 模拟API查询逻辑 ===')
category_id = 4

try:
    category = Category.objects.get(id=category_id)
    print(f'找到分类: {category.name} (ID: {category.id})')
    
    # 模拟API中的试卷查询
    print('\n=== 试卷查询测试 ===')
    
    # 测试1: 直接查询
    papers1 = ExamPaper.objects.filter(categories=category, is_active=True)
    print(f'方法1 - filter(categories=category): {papers1.count()}个试卷')
    
    # 测试2: 使用ID查询
    papers2 = ExamPaper.objects.filter(categories__id=category_id, is_active=True)
    print(f'方法2 - filter(categories__id={category_id}): {papers2.count()}个试卷')
    
    # 测试3: 使用in查询
    papers3 = ExamPaper.objects.filter(categories__in=[category], is_active=True)
    print(f'方法3 - filter(categories__in=[category]): {papers3.count()}个试卷')
    
    # 显示前3个试卷的详细信息
    print('\n=== 前3个试卷详情 ===')
    for paper in papers1[:3]:
        print(f'ID:{paper.id}, 标题:{paper.title}, 描述:{paper.description[:50] if paper.description else "无"}')
        print(f'  时长:{paper.duration}分钟, 总分:{paper.total_score}, 题目数:{paper.question_count}')
        print(f'  试卷类型:{paper.paper_type}, 创建时间:{paper.create_time}')
        print()
        
except Category.DoesNotExist:
    print(f'分类ID {category_id} 不存在')
except Exception as e:
    print(f'查询出错: {e}')