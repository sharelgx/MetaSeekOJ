#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实导入测试脚本
模拟前端发送的完整数据格式
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.import_serializers import ChoiceQuestionImportSerializer
from choice_question.models import ChoiceQuestion, Category, QuestionTag
from account.models import User

def test_real_import():
    """
    测试真实的导入数据格式（模拟前端发送的数据）
    """
    print("=== 真实导入测试 ===")
    
    # 模拟前端发送的数据格式
    import_data = {
        "questions": [
            {
                "title": "Python基础题目",
                "description": "以下哪个是Python的数据类型？",
                "question_type": "single",  # 前端现在发送字符串格式
                "options": [
                    {"content": "String", "is_correct": False},
                    {"content": "Integer", "is_correct": False},
                    {"content": "List", "is_correct": False},
                    {"content": "All of the above", "is_correct": True}
                ],
                "correct_answer": "D",
                "explanation": "Python中String、Integer、List都是基本数据类型。",
                "difficulty": "easy",
                "visible": True
            },
            {
                "title": "前端框架多选题",
                "description": "以下哪些是前端框架？",
                "question_type": "multiple",
                "options": [
                    {"content": "Vue.js", "is_correct": True},
                    {"content": "React", "is_correct": True},
                    {"content": "Django", "is_correct": False},
                    {"content": "Angular", "is_correct": True}
                ],
                "correct_answer": "A,B,D",
                "explanation": "Vue.js、React、Angular都是前端框架，Django是后端框架。",
                "difficulty": "medium",
                "visible": True
            }
        ],
        "category_id": 9,  # 测试分类
        "tag_ids": [2],    # 测试标签
        "language": "Python"  # 这个字段应该被忽略
    }
    
    print("1. 测试数据:")
    print(f"题目数量: {len(import_data['questions'])}")
    print(f"分类ID: {import_data['category_id']}")
    print(f"标签IDs: {import_data['tag_ids']}")
    print(f"编程语言: {import_data['language']}")
    
    # 获取测试用户
    try:
        user = User.objects.filter(is_super_admin=True).first()
        if not user:
            user = User.objects.first()
        print(f"使用用户: {user.username if user else 'None'}")
    except:
        user = None
        print("未找到用户")
    
    # 测试序列化器验证
    print("\n2. 测试序列化器验证:")
    serializer = ChoiceQuestionImportSerializer(data=import_data)
    is_valid = serializer.is_valid()
    print(f"验证结果: {is_valid}")
    
    if not is_valid:
        print(f"验证错误: {serializer.errors}")
        return
    
    print("验证通过")
    
    # 测试创建过程
    print("\n3. 测试创建过程:")
    try:
        # 添加创建者信息
        validated_data = serializer.validated_data.copy()
        if user:
            validated_data['created_by'] = user
        
        result = serializer.create(validated_data)
        print(f"创建结果: 成功创建 {result['success_count']} 道题目")
        
        if result['errors']:
            print(f"创建错误: {result['errors']}")
        
        # 检查创建的题目
        for question in result['created_questions']:
            print(f"\n题目ID: {question.id}")
            print(f"题目标题: {question.title}")
            print(f"题目类型: {question.question_type}")
            print(f"题目难度: {question.difficulty}")
            print(f"题目分类: {question.category.name if question.category else 'None'}")
            print(f"题目标签: {[tag.name for tag in question.tags.all()]}")
            print(f"选项数量: {len(question.options)}")
            print(f"正确答案: {question.correct_answer}")
            
    except Exception as e:
        print(f"创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 真实导入测试完成 ===")

if __name__ == '__main__':
    test_real_import()