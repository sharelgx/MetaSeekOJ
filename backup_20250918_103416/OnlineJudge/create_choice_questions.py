#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ChoiceQuestion, Category
from account.models import User

def create_sample_choice_questions():
    """创建示例选择题数据"""
    
    # 获取或创建管理员用户
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # 获取或创建分类
    category, created = Category.objects.get_or_create(
        name='编程基础',
        defaults={'description': '编程基础知识'}
    )
    
    # 创建选择题数据
    questions_data = [
        {
            '_id': 'CQ001',
            'title': 'Python中哪个关键字用于定义函数？',
            'description': '请选择正确的Python函数定义关键字',
            'question_type': 'single',
            'options': '[{"key": "A", "text": "function"}, {"key": "B", "text": "def"}, {"key": "C", "text": "func"}, {"key": "D", "text": "define"}]',
            'correct_answer': 'B',
            'explanation': 'Python中使用def关键字来定义函数',
            'difficulty': 'easy',
            'score': 10,
            'language': 'python'
        },
        {
            '_id': 'CQ002',
            'title': '以下哪些是Python的数据类型？',
            'description': '请选择所有正确的Python数据类型',
            'question_type': 'multiple',
            'options': '[{"key": "A", "text": "int"}, {"key": "B", "text": "string"}, {"key": "C", "text": "list"}, {"key": "D", "text": "dict"}]',
            'correct_answer': 'A,C,D',
            'explanation': 'Python中int、list、dict都是基本数据类型，但string应该是str',
            'difficulty': 'medium',
            'score': 15,
            'language': 'python'
        },
        {
            '_id': 'CQ003',
            'title': 'C++中哪个操作符用于访问指针指向的对象？',
            'description': '请选择正确的C++指针解引用操作符',
            'question_type': 'single',
            'options': '[{"key": "A", "text": "&"}, {"key": "B", "text": "*"}, {"key": "C", "text": "->"}, {"key": "D", "text": "."}]',
            'correct_answer': 'B',
            'explanation': 'C++中*操作符用于解引用指针，获取指针指向的对象',
            'difficulty': 'medium',
            'score': 12,
            'language': 'cpp'
        }
    ]
    
    created_count = 0
    for question_data in questions_data:
        question, created = ChoiceQuestion.objects.get_or_create(
            _id=question_data['_id'],
            defaults={
                **question_data,
                'category': category,
                'created_by': admin_user
            }
        )
        if created:
            created_count += 1
            print(f"创建选择题: {question._id} - {question.title}")
        else:
            print(f"选择题已存在: {question._id} - {question.title}")
    
    print(f"\n总共创建了 {created_count} 道选择题")
    print(f"ChoiceQuestion表总数据量: {ChoiceQuestion.objects.count()}")

if __name__ == '__main__':
    create_sample_choice_questions()