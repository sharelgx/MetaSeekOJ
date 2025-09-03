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
    
    id = serializers.CharField(required=False, allow_blank=True)
    question = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=['single', 'multiple'], required=True)
    options = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        required=True
    )
    correct = serializers.CharField(required=True)
    explanation = serializers.CharField(required=False, allow_blank=True)
    
    def validate_correct(self, value):
        """验证正确答案格式"""
        if not value:
            raise serializers.ValidationError("正确答案不能为空")
        
        # 支持单个字母或多个字母（用逗号分隔）
        if ',' in value:
            answers = [ans.strip().upper() for ans in value.split(',')]
        else:
            answers = [value.strip().upper()]
        
        # 验证答案格式
        for answer in answers:
            if not re.match(r'^[A-Z]$', answer):
                raise serializers.ValidationError(f"答案格式错误: {answer}，应为A-Z的单个字母")
        
        return ','.join(answers) if len(answers) > 1 else answers[0]
    
    def validate(self, attrs):
        """交叉验证"""
        options = attrs.get('options', [])
        correct = attrs.get('correct', '')
        question_type = attrs.get('type')
        
        # 验证正确答案是否在选项范围内
        if ',' in correct:
            correct_answers = correct.split(',')
        else:
            correct_answers = [correct]
        
        for answer in correct_answers:
            answer_index = ord(answer) - ord('A')
            if answer_index >= len(options):
                raise serializers.ValidationError(
                    f"正确答案 {answer} 超出选项范围（共{len(options)}个选项）"
                )
        
        # 验证题目类型与答案数量的匹配
        if question_type == 'single' and len(correct_answers) > 1:
            raise serializers.ValidationError("单选题只能有一个正确答案")
        elif question_type == 'multiple' and len(correct_answers) == 1:
            # 多选题允许只有一个正确答案，但给出警告
            pass
        
        return attrs
    
    def to_internal_value(self, data):
        """转换为内部格式"""
        validated_data = super().to_internal_value(data)
        
        # 转换为系统格式
        question_data = self.convert_to_system_format(validated_data)
        return question_data
    
    def convert_to_system_format(self, data):
        """转换为系统内部格式"""
        # 从question字段提取前50个字符作为title
        question_text = data['question']
        title = question_text[:50] + ('...' if len(question_text) > 50 else '')
        
        # 转换选项格式
        options = []
        correct_answers = data['correct'].split(',') if ',' in data['correct'] else [data['correct']]
        
        for i, option_text in enumerate(data['options']):
            option_letter = chr(ord('A') + i)
            options.append({
                'key': option_letter,
                'text': option_text,
                'is_correct': option_letter in correct_answers
            })
        
        return {
            'title': title,
            'description': question_text,
            'question_type': data['type'],
            'difficulty': 'Mid',  # 默认中等难度
            'score': 2,  # 默认2分
            'options': options,
            'explanation': data.get('explanation', ''),
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