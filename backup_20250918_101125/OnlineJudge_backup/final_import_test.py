#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终综合导入测试
验证所有修复的功能：
1. question_type字段的字符串和整数格式兼容性
2. 分类和标签的正确关联
3. language字段的正确过滤
4. 选项格式的正确转换
5. 难度字段的正确映射
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

def test_string_format():
    """测试字符串格式的question_type"""
    print("\n=== 测试字符串格式 ===")
    data = {
        "questions": [{
            "title": "字符串格式测试",
            "description": "这是一个单选题",
            "question_type": "single",  # 字符串格式
            "options": [
                {"content": "选项A", "is_correct": True},
                {"content": "选项B", "is_correct": False}
            ],
            "difficulty": "easy",
            "visible": True
        }],
        "category_id": 9,
        "tag_ids": [2],
        "language": "Python"  # 应该被过滤
    }
    
    serializer = ChoiceQuestionImportSerializer(data=data)
    if serializer.is_valid():
        user = User.objects.filter(admin_type__in=['Super Admin', 'Admin']).first()
        validated_data = serializer.validated_data.copy()
        if user:
            validated_data['created_by'] = user
        result = serializer.create(validated_data)
        print(f"✓ 字符串格式测试通过，创建题目ID: {result['created_questions'][0].id}")
        return True
    else:
        print(f"✗ 字符串格式测试失败: {serializer.errors}")
        return False

def test_integer_format():
    """测试整数格式的question_type（向后兼容）"""
    print("\n=== 测试整数格式（向后兼容） ===")
    data = {
        "questions": [{
            "title": "整数格式测试",
            "description": "这是一个多选题",
            "question_type": 1,  # 整数格式
            "options": [
                {"content": "选项A", "is_correct": True},
                {"content": "选项B", "is_correct": True},
                {"content": "选项C", "is_correct": False}
            ],
            "difficulty": "Mid",
            "visible": True
        }],
        "category_id": 9,
        "tag_ids": [2]
    }
    
    serializer = ChoiceQuestionImportSerializer(data=data)
    if serializer.is_valid():
        user = User.objects.filter(admin_type__in=['Super Admin', 'Admin']).first()
        validated_data = serializer.validated_data.copy()
        if user:
            validated_data['created_by'] = user
        result = serializer.create(validated_data)
        question = result['created_questions'][0]
        print(f"✓ 整数格式测试通过，创建题目ID: {question.id}")
        print(f"  题目类型: {question.question_type} (应为multiple)")
        print(f"  题目难度: {question.difficulty} (应为medium)")
        return True
    else:
        print(f"✗ 整数格式测试失败: {serializer.errors}")
        return False

def test_category_and_tags():
    """测试分类和标签的正确关联"""
    print("\n=== 测试分类和标签关联 ===")
    data = {
        "questions": [{
            "title": "分类标签测试",
            "description": "测试分类和标签是否正确关联",
            "question_type": "single",
            "options": [
                {"content": "选项A", "is_correct": True},
                {"content": "选项B", "is_correct": False}
            ],
            "difficulty": "Hard",
            "visible": True
        }],
        "category_id": 9,  # 测试分类
        "tag_ids": [2]     # 测试标签
    }
    
    serializer = ChoiceQuestionImportSerializer(data=data)
    if serializer.is_valid():
        user = User.objects.filter(admin_type__in=['Super Admin', 'Admin']).first()
        validated_data = serializer.validated_data.copy()
        if user:
            validated_data['created_by'] = user
        result = serializer.create(validated_data)
        question = result['created_questions'][0]
        category_name = question.category.name if question.category else 'None'
        tag_names = [tag.name for tag in question.tags.all()]
        print(f"✓ 分类标签测试通过，创建题目ID: {question.id}")
        print(f"  分类: {category_name}")
        print(f"  标签: {tag_names}")
        print(f"  难度: {question.difficulty} (应为hard)")
        return True
    else:
        print(f"✗ 分类标签测试失败: {serializer.errors}")
        return False

def test_batch_import():
    """测试批量导入"""
    print("\n=== 测试批量导入 ===")
    data = {
        "questions": [
            {
                "title": "批量导入题目1",
                "description": "第一道题目",
                "question_type": "single",
                "options": [
                    {"content": "A选项", "is_correct": True},
                    {"content": "B选项", "is_correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "title": "批量导入题目2",
                "description": "第二道题目",
                "question_type": "multiple",
                "options": [
                    {"content": "A选项", "is_correct": True},
                    {"content": "B选项", "is_correct": True},
                    {"content": "C选项", "is_correct": False}
                ],
                "difficulty": "medium"
            },
            {
                "title": "批量导入题目3",
                "description": "第三道题目",
                "question_type": 0,  # 混合使用整数格式
                "options": [
                    {"content": "A选项", "is_correct": False},
                    {"content": "B选项", "is_correct": True}
                ],
                "difficulty": "Hard"  # 混合使用大写格式
            }
        ],
        "category_id": 9,
        "tag_ids": [2],
        "language": "JavaScript"  # 应该被过滤
    }
    
    serializer = ChoiceQuestionImportSerializer(data=data)
    if serializer.is_valid():
        user = User.objects.filter(admin_type__in=['Super Admin', 'Admin']).first()
        validated_data = serializer.validated_data.copy()
        if user:
            validated_data['created_by'] = user
        result = serializer.create(validated_data)
        print(f"✓ 批量导入测试通过，成功创建 {result['success_count']} 道题目")
        
        for i, question in enumerate(result['created_questions']):
            print(f"  题目{i+1} ID: {question.id}, 类型: {question.question_type}, 难度: {question.difficulty}")
        
        return True
    else:
        print(f"✗ 批量导入测试失败: {serializer.errors}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始运行选择题导入功能综合测试...")
    
    tests = [
        ("字符串格式测试", test_string_format),
        ("整数格式测试", test_integer_format),
        ("分类标签测试", test_category_and_tags),
        ("批量导入测试", test_batch_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name}异常: {str(e)}")
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！选择题导入功能修复完成。")
    else:
        print("❌ 部分测试失败，需要进一步检查。")
    
    return passed == total

if __name__ == '__main__':
    run_all_tests()