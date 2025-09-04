#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择题导入功能调试脚本
用于分析导入过程中的数据处理和错误信息
"""

import json
import logging
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ChoiceQuestion, QuestionTag, ChoiceQuestionCategory
from .serializers import ChoiceQuestionCreateSerializer
from .import_serializers import ChoiceQuestionImportSerializer

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_import_process():
    """
    调试导入过程
    """
    print("=== 选择题导入功能调试 ===")
    
    # 测试数据
    test_data = {
        "questions": [
            {
                "id": "DEBUG_001",
                "type": "single",
                "question": "调试测试题目",
                "options": [
                    "选项A",
                    "选项B", 
                    "选项C",
                    "选项D"
                ],
                "correct": "A",
                "explanation": "这是一道调试测试题目。"
            }
        ],
        "category_id": None,
        "tag_ids": []
    }
    
    print("\n1. 测试数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    # 测试序列化器
    print("\n2. 测试导入序列化器:")
    try:
        import_serializer = ChoiceQuestionImportSerializer(data=test_data)
        print(f"序列化器验证结果: {import_serializer.is_valid()}")
        if not import_serializer.is_valid():
            print(f"验证错误: {import_serializer.errors}")
        else:
            print("序列化器验证通过")
            
            # 测试创建过程
            print("\n3. 测试创建过程:")
            try:
                result = import_serializer.save()
                print(f"创建结果: {result}")
            except Exception as e:
                print(f"创建过程出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"序列化器测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试单个题目序列化器
    print("\n4. 测试单个题目创建序列化器:")
    question_data = {
        "title": "调试测试题目",
        "description": "调试测试题目",
        "question_type": 0,
        "options": [
            {"content": "选项A", "is_correct": True},
            {"content": "选项B", "is_correct": False},
            {"content": "选项C", "is_correct": False},
            {"content": "选项D", "is_correct": False}
        ],
        "correct_answer": "A",
        "explanation": "这是一道调试测试题目。",
        "difficulty": "Easy",
        "visible": True
    }
    
    try:
        create_serializer = ChoiceQuestionCreateSerializer(data=question_data)
        print(f"创建序列化器验证结果: {create_serializer.is_valid()}")
        if not create_serializer.is_valid():
            print(f"验证错误: {create_serializer.errors}")
        else:
            print("创建序列化器验证通过")
    except Exception as e:
        print(f"创建序列化器测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 检查模型字段
    print("\n5. 检查ChoiceQuestion模型字段:")
    try:
        fields = [f.name for f in ChoiceQuestion._meta.get_fields()]
        print(f"模型字段: {fields}")
        
        # 检查tags字段
        tags_field = ChoiceQuestion._meta.get_field('tags')
        print(f"tags字段类型: {type(tags_field)}")
        print(f"tags字段关联模型: {tags_field.related_model}")
        
    except Exception as e:
        print(f"模型字段检查出错: {str(e)}")
    
    # 检查现有数据
    print("\n6. 检查现有数据:")
    try:
        question_count = ChoiceQuestion.objects.count()
        tag_count = QuestionTag.objects.count()
        category_count = ChoiceQuestionCategory.objects.count()
        
        print(f"现有题目数量: {question_count}")
        print(f"现有标签数量: {tag_count}")
        print(f"现有分类数量: {category_count}")
        
        if tag_count > 0:
            tags = QuestionTag.objects.all()[:5]
            print("前5个标签:")
            for tag in tags:
                print(f"  - ID: {tag.id}, 名称: {tag.name}")
                
        if category_count > 0:
            categories = ChoiceQuestionCategory.objects.all()[:5]
            print("前5个分类:")
            for category in categories:
                print(f"  - ID: {category.id}, 名称: {category.name}")
                
    except Exception as e:
        print(f"数据检查出错: {str(e)}")
    
    print("\n=== 调试完成 ===")

# 这个脚本需要通过Django管理命令运行
# 使用方法: python3 manage.py shell < choice_question/debug_import.py