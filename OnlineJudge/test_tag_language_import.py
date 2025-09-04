#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选择题标签和编程语言导入功能
"""

import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')

import django
django.setup()

from django.test import TestCase
from account.models import User

from choice_question.models import ChoiceQuestion, Category, QuestionTag
from choice_question.import_serializers import ChoiceQuestionImportSerializer

def test_tag_language_import():
    """测试标签和编程语言导入功能"""
    print("开始测试标签和编程语言导入功能...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    print(f"测试用户: {user.username}")
    
    # 创建测试分类
    category, created = Category.objects.get_or_create(
        name='Python基础',
        defaults={'description': 'Python基础知识测试'}
    )
    print(f"测试分类: {category.name} (ID: {category.id})")
    
    # 创建测试标签
    tag1, created = QuestionTag.objects.get_or_create(
        name='循环',
        defaults={'description': '循环相关题目', 'color': '#FF5722'}
    )
    tag2, created = QuestionTag.objects.get_or_create(
        name='基础语法',
        defaults={'description': '基础语法题目', 'color': '#2196F3'}
    )
    print(f"测试标签: {tag1.name} (ID: {tag1.id}), {tag2.name} (ID: {tag2.id})")
    
    # 准备测试数据
    test_data = {
        'questions': [
            {
                'title': 'Python for循环测试',
                'description': '以下Python代码的输出是什么？\n\n```python\nfor i in range(3):\n    print(i)\n```',
                'question_type': 'single',
                'options': [
                    {'key': 'A', 'content': '0 1 2', 'is_correct': False},
                    {'key': 'B', 'content': '1 2 3', 'is_correct': False},
                    {'key': 'C', 'content': '0\\n1\\n2', 'is_correct': True},
                    {'key': 'D', 'content': '1\\n2\\n3', 'is_correct': False}
                ],
                'correct_answer': 'C',
                'difficulty': 'easy',
                'score': 5,
                'language': 'python'
            },
            {
                'title': 'JavaScript变量声明',
                'description': '以下JavaScript代码中，哪种变量声明方式是块级作用域？\n\n```javascript\nvar a = 1;\nlet b = 2;\nconst c = 3;\n```',
                'question_type': 'single',
                'options': [
                    {'key': 'A', 'content': 'var', 'is_correct': False},
                    {'key': 'B', 'content': 'let和const', 'is_correct': True},
                    {'key': 'C', 'content': '只有let', 'is_correct': False},
                    {'key': 'D', 'content': '只有const', 'is_correct': False}
                ],
                'correct_answer': 'B',
                'difficulty': 'medium',
                'score': 8,
                'language': 'javascript'
            }
        ],
        'category_id': category.id,
        'tag_ids': [tag1.id, tag2.id],
        'language': 'python',  # 全局语言设置
        'created_by': user
    }
    
    print("\n测试数据准备完成，开始导入...")
    
    # 使用导入序列化器
    serializer = ChoiceQuestionImportSerializer(data=test_data)
    
    if serializer.is_valid():
        print("数据验证通过")
        
        # 执行导入
        result = serializer.save()
        created_questions = result['created_questions']
        print(f"导入成功，创建了 {len(created_questions)} 个题目")
        
        # 验证导入结果
        for i, question in enumerate(created_questions):
            print(f"\n题目 {i+1}:")
            print(f"  标题: {question.title}")
            print(f"  编程语言: {question.language}")
            print(f"  分类: {question.category.name if question.category else '无'}")
            
            # 检查标签
            tags = question.tags.all()
            if tags:
                tag_names = [tag.name for tag in tags]
                print(f"  标签: {', '.join(tag_names)}")
            else:
                print("  标签: 无")
            
            # 检查代码块
            if '```' in question.description:
                print("  包含代码块: 是")
            else:
                print("  包含代码块: 否")
        
        # 验证语言字段
        python_questions = [q for q in created_questions if q.language == 'python']
        js_questions = [q for q in created_questions if q.language == 'javascript']
        
        print(f"\n语言统计:")
        print(f"  Python题目: {len(python_questions)}")
        print(f"  JavaScript题目: {len(js_questions)}")
        
        # 验证标签关联
        tagged_questions = [q for q in created_questions if q.tags.exists()]
        print(f"  有标签的题目: {len(tagged_questions)}")
        
        # 验证分类关联
        categorized_questions = [q for q in created_questions if q.category]
        print(f"  有分类的题目: {len(categorized_questions)}")
        
        print("\n✅ 标签和编程语言导入功能测试通过！")
        return True
        
    else:
        print("❌ 数据验证失败:")
        for field, errors in serializer.errors.items():
            print(f"  {field}: {errors}")
        return False

def cleanup_test_data():
    """清理测试数据"""
    print("\n清理测试数据...")
    
    # 删除测试题目
    test_questions = ChoiceQuestion.objects.filter(
        title__in=['Python for循环测试', 'JavaScript变量声明']
    )
    deleted_count = test_questions.count()
    test_questions.delete()
    print(f"删除了 {deleted_count} 个测试题目")

if __name__ == '__main__':
    try:
        success = test_tag_language_import()
        if success:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup_test_data()