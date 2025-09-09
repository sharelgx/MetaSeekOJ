#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamPaper, Category

# 检查分类4的试卷情况
print('=== 试卷数据调试 ===')
print(f'试卷总数: {ExamPaper.objects.count()}')
print(f'分类ID=4的试卷数: {ExamPaper.objects.filter(categories=4).count()}')
print(f'活跃的分类4试卷数: {ExamPaper.objects.filter(categories=4, is_active=True).count()}')

print('\n=== 前3个分类4的活跃试卷 ===')
papers = ExamPaper.objects.filter(categories=4, is_active=True)[:3]
for p in papers:
    categories = list(p.categories.values_list('id', flat=True))
    print(f'ID:{p.id}, 标题:{p.title}, is_active:{p.is_active}, 分类:{categories}')

print('\n=== 分类4信息 ===')
try:
    category = Category.objects.get(id=4)
    print(f'分类4: ID={category.id}, 名称={category.name}, 父级={category.parent_id}')
except Category.DoesNotExist:
    print('分类4不存在')