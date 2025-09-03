# -*- coding: utf-8 -*-
"""
选择题导入序列化器
"""

from rest_framework import serializers
from .models import ChoiceQuestion, Category, QuestionTag
from .serializers import ChoiceQuestionCreateSerializer
import re


class ChoiceQuestionImportItemSerializer(serializers.Serializer):
    """单个选择题导入项序列化器"""
    
    # 支持前端发送的格式
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=True)
    question_type = serializers.IntegerField(required=True)
    difficulty = serializers.CharField(required=False, default='Mid')
    score = serializers.IntegerField(required=False, default=2)
    options = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        required=True
    )
    categories = serializers.ListField(required=False, default=list)
    tags = serializers.ListField(required=False, default=list)
    explanation = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, default='text')
    
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
        
        return value
    
    def validate_question_type(self, value):
        """验证题目类型"""
        if value not in [0, 1]:  # 0-单选，1-多选
            raise serializers.ValidationError("题目类型必须为0(单选)或1(多选)")
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
        
        # 转换为系统格式
        question_data = self.convert_to_system_format(validated_data)
        return question_data
    
    def convert_to_system_format(self, data):
        """转换为系统内部格式"""
        # 使用title字段，如果没有则从description提取
        title = data.get('title')
        if not title:
            # 从description字段提取前50个字符作为title
            description_text = data['description']
            # 移除HTML标签
            import re
            clean_text = re.sub(r'<[^>]+>', '', description_text)
            title = clean_text[:50] + ('...' if len(clean_text) > 50 else '')
        
        # 转换选项格式 - 使用ChoiceQuestionCreateSerializer期望的格式
        options = []
        correct_answers = []
        
        for i, option_data in enumerate(data['options']):
            option_letter = chr(ord('A') + i)
            options.append({
                'key': option_letter,
                'text': option_data['content']
            })
            
            # 收集正确答案
            if option_data.get('is_correct', False):
                correct_answers.append(option_letter)
        
        # 转换题目类型
        question_type_map = {0: 'single', 1: 'multiple'}
        question_type = question_type_map.get(data['question_type'], 'single')
        
        # 转换难度
        difficulty_map = {'Easy': 'easy', 'Mid': 'medium', 'Hard': 'hard'}
        difficulty = difficulty_map.get(data.get('difficulty', 'Mid'), 'medium')
        
        return {
            'title': title,
            'description': data['description'],
            'question_type': question_type,
            'difficulty': difficulty,
            'score': data.get('score', 2),
            'options': options,
            'correct_answer': ','.join(correct_answers) if len(correct_answers) > 1 else (correct_answers[0] if correct_answers else ''),
            'explanation': data.get('explanation', ''),
            'language': data.get('language', 'text'),
            'visible': True,
            'is_public': True
        }


class ChoiceQuestionImportSerializer(serializers.Serializer):
    """选择题批量导入序列化器"""
    
    questions = serializers.ListField(
        child=ChoiceQuestionImportItemSerializer(),
        min_length=1,
        required=True
    )
    category_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_category_id(self, value):
        """验证分类ID"""
        if value is not None:
            try:
                Category.objects.get(id=value)
            except Category.DoesNotExist:
                raise serializers.ValidationError("指定的分类不存在")
        return value
    
    def create(self, validated_data):
        """批量创建选择题"""
        questions_data = validated_data['questions']
        category_id = validated_data.get('category_id')
        created_by = validated_data.get('created_by')
        
        created_questions = []
        errors = []
        
        for index, question_data in enumerate(questions_data):
            try:
                # 添加分类
                if category_id:
                    question_data['category_id'] = category_id
                
                # 生成显示ID
                if not question_data.get('_id'):
                    import uuid
                    question_data['_id'] = str(uuid.uuid4())[:8].upper()
                
                # 使用现有的创建序列化器
                serializer = ChoiceQuestionCreateSerializer(data=question_data)
                if serializer.is_valid():
                    question = serializer.save(created_by=created_by)
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