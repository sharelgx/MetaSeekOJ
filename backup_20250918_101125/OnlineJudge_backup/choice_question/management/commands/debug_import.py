#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择题导入功能调试管理命令
"""

import json
from django.core.management.base import BaseCommand
from choice_question.models import ChoiceQuestion, QuestionTag, Category
from choice_question.serializers import ChoiceQuestionCreateSerializer
from choice_question.import_serializers import ChoiceQuestionImportSerializer

class Command(BaseCommand):
    help = '调试选择题导入功能'
    
    def handle(self, *args, **options):
        self.stdout.write("=== 选择题导入功能调试 ===")
        
        # 测试数据 - 使用前端发送的格式
        test_data = {
            "questions": [
                {
                    "title": "调试测试题目",
                    "description": "这是一道调试测试题目，用于测试导入功能。",
                    "question_type": 0,  # 单选题
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
            ],
            "category_id": None,
            "tag_ids": []
        }
        
        self.stdout.write("\n1. 测试数据:")
        self.stdout.write(json.dumps(test_data, indent=2, ensure_ascii=False))
        
        # 测试序列化器
        self.stdout.write("\n2. 测试导入序列化器:")
        try:
            import_serializer = ChoiceQuestionImportSerializer(data=test_data)
            self.stdout.write(f"序列化器验证结果: {import_serializer.is_valid()}")
            if not import_serializer.is_valid():
                self.stdout.write(f"验证错误: {import_serializer.errors}")
            else:
                self.stdout.write("序列化器验证通过")
                
                # 测试创建过程
                self.stdout.write("\n3. 测试创建过程:")
                try:
                    result = import_serializer.save()
                    self.stdout.write(f"创建结果: {result}")
                    
                    # 检查创建的题目
                    if 'created_questions' in result:
                        for question in result['created_questions']:
                            self.stdout.write(f"创建的题目ID: {question.id}")
                            self.stdout.write(f"题目标题: {question.title}")
                            self.stdout.write(f"题目标签: {list(question.tags.all())}")
                            self.stdout.write(f"题目分类: {question.category}")
                            
                except Exception as e:
                    self.stdout.write(f"创建过程出错: {str(e)}")
                    import traceback
                    self.stdout.write(traceback.format_exc())
                    
        except Exception as e:
            self.stdout.write(f"序列化器测试出错: {str(e)}")
            import traceback
            self.stdout.write(traceback.format_exc())
        
        # 测试单个题目序列化器
        self.stdout.write("\n4. 测试单个题目创建序列化器:")
        question_data = {
            "title": "调试测试题目",
            "description": "调试测试题目",
            "question_type": "single",  # 使用字符串格式
            "options": [
                {"key": "A", "text": "选项A"},
                {"key": "B", "text": "选项B"},
                {"key": "C", "text": "选项C"},
                {"key": "D", "text": "选项D"}
            ],
            "correct_answer": "A",
            "explanation": "这是一道调试测试题目。",
            "difficulty": "easy",  # 使用小写格式
            "visible": True
        }
        
        try:
            create_serializer = ChoiceQuestionCreateSerializer(data=question_data)
            self.stdout.write(f"创建序列化器验证结果: {create_serializer.is_valid()}")
            if not create_serializer.is_valid():
                self.stdout.write(f"验证错误: {create_serializer.errors}")
            else:
                self.stdout.write("创建序列化器验证通过")
                
                # 检查序列化器字段
                self.stdout.write(f"序列化器字段: {list(create_serializer.fields.keys())}")
                self.stdout.write(f"序列化器排除字段: {getattr(create_serializer.Meta, 'exclude', [])}")
                
        except Exception as e:
            self.stdout.write(f"创建序列化器测试出错: {str(e)}")
            import traceback
            self.stdout.write(traceback.format_exc())
        
        # 检查模型字段
        self.stdout.write("\n5. 检查ChoiceQuestion模型字段:")
        try:
            fields = [f.name for f in ChoiceQuestion._meta.get_fields()]
            self.stdout.write(f"模型字段: {fields}")
            
            # 检查tags字段
            tags_field = ChoiceQuestion._meta.get_field('tags')
            self.stdout.write(f"tags字段类型: {type(tags_field)}")
            self.stdout.write(f"tags字段关联模型: {tags_field.related_model}")
            
        except Exception as e:
            self.stdout.write(f"模型字段检查出错: {str(e)}")
        
        # 检查现有数据
        self.stdout.write("\n6. 检查现有数据:")
        try:
            question_count = ChoiceQuestion.objects.count()
            tag_count = QuestionTag.objects.count()
            category_count = Category.objects.count()
            
            self.stdout.write(f"现有题目数量: {question_count}")
            self.stdout.write(f"现有标签数量: {tag_count}")
            self.stdout.write(f"现有分类数量: {category_count}")
            
            if tag_count > 0:
                tags = QuestionTag.objects.all()[:5]
                self.stdout.write("前5个标签:")
                for tag in tags:
                    self.stdout.write(f"  - ID: {tag.id}, 名称: {tag.name}")
                    
            if category_count > 0:
                categories = Category.objects.all()[:5]
                self.stdout.write("前5个分类:")
                for category in categories:
                    self.stdout.write(f"  - ID: {category.id}, 名称: {category.name}")
                    
        except Exception as e:
            self.stdout.write(f"数据检查出错: {str(e)}")
        
        # 测试带标签和分类的导入
        self.stdout.write("\n7. 测试带标签和分类的导入:")
        try:
            # 创建测试标签和分类
            test_tag, created = QuestionTag.objects.get_or_create(
                name="测试标签",
                defaults={"tag_type": "knowledge"}
            )
            test_category, created = Category.objects.get_or_create(
                name="测试分类"
            )
            
            self.stdout.write(f"测试标签ID: {test_tag.id}")
            self.stdout.write(f"测试分类ID: {test_category.id}")
            
            # 测试带标签和分类的导入数据
            test_data_with_tags = {
                "questions": [
                    {
                        "title": "带标签和分类的测试题目",
                        "description": "这是一道带标签和分类的测试题目，用于测试分类和标签功能。",
                        "question_type": 0,  # 单选题
                        "options": [
                            {"content": "选项A", "is_correct": False},
                            {"content": "选项B", "is_correct": True},
                            {"content": "选项C", "is_correct": False},
                            {"content": "选项D", "is_correct": False}
                        ],
                        "correct_answer": "B",
                        "explanation": "这是一道带标签和分类的测试题目。",
                        "difficulty": "Easy",
                        "visible": True
                    }
                ],
                "category_id": test_category.id,
                "tag_ids": [test_tag.id]
            }
            
            import_serializer = ChoiceQuestionImportSerializer(data=test_data_with_tags)
            self.stdout.write(f"带标签分类的序列化器验证结果: {import_serializer.is_valid()}")
            if not import_serializer.is_valid():
                self.stdout.write(f"验证错误: {import_serializer.errors}")
            else:
                result = import_serializer.save()
                self.stdout.write(f"带标签分类的创建结果: {result}")
                
                # 检查创建的题目
                if 'created_questions' in result:
                    for question in result['created_questions']:
                        self.stdout.write(f"题目ID: {question.id}")
                        self.stdout.write(f"题目分类: {question.category}")
                        self.stdout.write(f"题目标签: {[tag.name for tag in question.tags.all()]}")
                        
        except Exception as e:
            self.stdout.write(f"带标签分类测试出错: {str(e)}")
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write("\n=== 调试完成 ===")