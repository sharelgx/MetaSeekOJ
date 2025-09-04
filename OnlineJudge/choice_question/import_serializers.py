# -*- coding: utf-8 -*-
"""
选择题导入序列化器
"""

from rest_framework import serializers
from .models import ChoiceQuestion, Category, QuestionTag
from .serializers import ChoiceQuestionCreateSerializer
import re


class QuestionTypeField(serializers.Field):
    """自定义题目类型字段，支持字符串和整数格式"""
    
    def to_internal_value(self, data):
        """将输入数据转换为内部值"""
        # 支持字符串格式和整数格式
        if isinstance(data, str):
            if data not in ['single', 'multiple']:
                raise serializers.ValidationError("题目类型必须为'single'(单选)或'multiple'(多选)")
        elif isinstance(data, int):
            if data not in [0, 1]:  # 0-单选，1-多选
                raise serializers.ValidationError("题目类型必须为0(单选)或1(多选)")
        else:
            # 尝试转换字符串形式的数字
            try:
                int_value = int(data)
                if int_value not in [0, 1]:
                    raise serializers.ValidationError("题目类型必须为0(单选)或1(多选)")
            except (ValueError, TypeError):
                raise serializers.ValidationError("题目类型格式错误")
        return data
    
    def to_representation(self, value):
        """将内部值转换为输出格式"""
        return value


class ChoiceQuestionImportItemSerializer(serializers.Serializer):
    """单个选择题导入项序列化器 - 处理前端发送的格式"""
    
    # 前端发送的格式
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=True)
    question_type = QuestionTypeField(required=True)
    difficulty = serializers.CharField(required=False, default='Easy')
    score = serializers.IntegerField(required=False, default=2)
    options = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        required=True
    )
    correct_answer = serializers.CharField(required=False, allow_blank=True)
    explanation = serializers.CharField(required=False, allow_blank=True)
    visible = serializers.BooleanField(required=False, default=True)
    language = serializers.CharField(required=False, allow_blank=True)
    
    def validate_options(self, value):
        """验证选项格式"""
        if not value or len(value) < 2:
            raise serializers.ValidationError("至少需要2个选项")
        
        for i, option in enumerate(value):
            if not isinstance(option, dict):
                raise serializers.ValidationError(f"选项{i+1}格式错误，应为字典")
            if 'content' not in option:
                raise serializers.ValidationError(f"选项{i+1}缺少content字段")
            if 'is_correct' not in option:
                raise serializers.ValidationError(f"选项{i+1}缺少is_correct字段")
            # 验证content字段不能为空
            if not option['content'] or not str(option['content']).strip():
                raise serializers.ValidationError(f"选项{i+1}的内容不能为空")
            # 验证is_correct字段必须是布尔值
            if not isinstance(option['is_correct'], bool):
                raise serializers.ValidationError(f"选项{i+1}的is_correct字段必须是布尔值")
        
        return value
    

    
    def validate(self, attrs):
        """交叉验证"""
        options = attrs.get('options', [])
        question_type = attrs.get('question_type')
        
        # 统计正确答案数量
        correct_count = sum(1 for option in options if option.get('is_correct', False))
        
        # 验证正确答案数量
        if question_type == 0:  # 单选题
            if correct_count != 1:
                raise serializers.ValidationError("单选题必须有且仅有一个正确答案")
        elif question_type == 1:  # 多选题
            if correct_count < 2:
                raise serializers.ValidationError("多选题至少需要2个正确答案")
        
        return attrs
    
    def to_internal_value(self, data):
        """转换为内部格式"""
        validated_data = super().to_internal_value(data)
        
        # 直接返回前端格式的数据，因为前端已经转换为正确格式
        return self.convert_to_create_format(validated_data)
    
    def convert_to_create_format(self, data):
        """转换为ChoiceQuestionCreateSerializer期望的格式"""
        # 转换选项格式
        options = []
        for i, option_data in enumerate(data['options']):
            option_letter = chr(ord('A') + i)
            options.append({
                'key': option_letter,
                'text': option_data['content']
            })
        
        # 转换题目类型 - 支持字符串和整数格式
        question_type = data['question_type']
        if isinstance(question_type, int):
            question_type_map = {0: 'single', 1: 'multiple'}
            question_type = question_type_map.get(question_type, 'single')
        # 如果已经是字符串格式，直接使用
        
        # 转换难度
        difficulty_map = {'Easy': 'easy', 'Mid': 'medium', 'Hard': 'hard'}
        difficulty = difficulty_map.get(data.get('difficulty', 'Easy'), 'easy')
        
        # 生成正确答案字符串
        correct_answers = []
        for i, option in enumerate(data['options']):
            if option.get('is_correct', False):
                correct_answers.append(chr(ord('A') + i))
        correct_answer = ''.join(correct_answers) if correct_answers else 'A'
        
        # 过滤掉模型中不存在的字段（如language）
        result = {
            'title': data.get('title', ''),
            'description': data['description'],
            'question_type': question_type,
            'difficulty': difficulty,
            'score': data.get('score', 2),
            'options': options,
            'correct_answer': correct_answer,
            'explanation': data.get('explanation', ''),
            'visible': data.get('visible', True),
            'is_public': True,
            'language': data.get('language', '')
        }
        
        return result


class ChoiceQuestionImportSerializer(serializers.Serializer):
    """选择题批量导入序列化器"""
    
    questions = serializers.ListField(
        child=ChoiceQuestionImportItemSerializer(),
        min_length=1,
        required=True
    )
    category_id = serializers.IntegerField(required=False, allow_null=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list
    )
    
    def validate_category_id(self, value):
        """验证分类ID"""
        if value is not None:
            try:
                Category.objects.get(id=value)
            except Category.DoesNotExist:
                raise serializers.ValidationError("指定的分类不存在")
        return value
    
    def validate_tag_ids(self, value):
        """验证标签ID列表"""
        if value:
            existing_tags = QuestionTag.objects.filter(id__in=value)
            existing_ids = set(existing_tags.values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"以下标签ID不存在: {list(invalid_ids)}")
        return value
    
    def create(self, validated_data):
        """批量创建选择题"""
        questions_data = validated_data['questions']
        category_id = validated_data.get('category_id')
        tag_ids = validated_data.get('tag_ids', [])
        language = validated_data.get('language')
        created_by = validated_data.get('created_by')
        
        created_questions = []
        errors = []
        
        for index, question_data in enumerate(questions_data):
            try:
                # 添加分类
                if category_id:
                    question_data['category'] = category_id
                
                # 添加编程语言
                if language and not question_data.get('language'):
                    question_data['language'] = language
                
                # 生成显示ID
                if not question_data.get('_id'):
                    import uuid
                    question_data['_id'] = str(uuid.uuid4())[:8].upper()
                
                # 使用现有的创建序列化器
                serializer = ChoiceQuestionCreateSerializer(data=question_data)
                if serializer.is_valid():
                    question = serializer.save(created_by=created_by)
                    
                    # 添加标签
                    if tag_ids:
                        question.tags.set(tag_ids)
                    
                    created_questions.append(question)
                else:
                    errors.append({
                        'index': index + 1,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'index': index + 1,
                    'errors': str(e)
                })
        
        return {
            'created_questions': created_questions,
            'errors': errors,
            'success_count': len(created_questions),
            'total_count': len(questions_data)
        }