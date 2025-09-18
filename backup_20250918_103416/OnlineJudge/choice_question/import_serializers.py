# -*- coding: utf-8 -*-
"""
选择题导入序列化器
"""

from rest_framework import serializers
from .models import ChoiceQuestion, Category, QuestionTag
from .api.serializers import ChoiceQuestionCreateSerializer
import re
import json
from bs4 import BeautifulSoup


def process_html_with_language(html_content, language):
    """
    处理HTML内容，为代码块添加data-lang属性
    """
    if not html_content or not language:
        return html_content
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找所有的pre标签（代码块）
    pre_tags = soup.find_all('pre')
    
    for pre_tag in pre_tags:
        # 如果pre标签没有data-lang属性，则添加
        if not pre_tag.get('data-lang'):
            pre_tag['data-lang'] = language
    
    return str(soup)


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
    """单个选择题导入项序列化器 - 处理多种格式"""
    
    # 支持多种字段名格式
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    question = serializers.CharField(required=False, allow_blank=True)  # 兼容字段
    question_type = QuestionTypeField(required=False)
    type = serializers.CharField(required=False, allow_blank=True)  # 兼容字段
    difficulty = serializers.CharField(required=False, default='Easy')
    score = serializers.IntegerField(required=False, default=2)
    options = serializers.ListField(
        child=serializers.JSONField(),  # 支持字符串和字典
        min_length=2,
        required=True
    )
    correct_answer = serializers.CharField(required=False, allow_blank=True)
    correct = serializers.CharField(required=False, allow_blank=True)  # 兼容字段
    explanation = serializers.CharField(required=False, allow_blank=True)
    visible = serializers.BooleanField(required=False, default=True)
    language = serializers.CharField(required=False, allow_blank=True)
    
    def validate_options(self, value):
        """验证选项格式 - 支持字符串数组和字典数组"""
        if not value or len(value) < 2:
            raise serializers.ValidationError("至少需要2个选项")
        
        for i, option in enumerate(value):
            if isinstance(option, str):
                # 字符串格式，验证不为空
                if not option.strip():
                    raise serializers.ValidationError(f"选项{i+1}的内容不能为空")
            elif isinstance(option, dict):
                # 字典格式，按原来的逻辑验证
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
            else:
                raise serializers.ValidationError(f"选项{i+1}格式错误，应为字符串或字典")
        
        return value
    

    
    def validate(self, attrs):
        """交叉验证"""
        # 确保必要字段存在
        description = attrs.get('description') or attrs.get('question')
        if not description:
            raise serializers.ValidationError("题目描述不能为空（description或question字段）")
        
        # 确定题目类型
        question_type = attrs.get('question_type')
        if question_type is None:
            type_str = attrs.get('type', 'single')
            if type_str == 'single':
                question_type = 0
            elif type_str == 'multiple':
                question_type = 1
            else:
                question_type = 0  # 默认单选
        
        options = attrs.get('options', [])
        
        # 如果选项是字符串数组，需要根据correct字段确定正确答案
        if options and isinstance(options[0], str):
            correct_answer = attrs.get('correct_answer') or attrs.get('correct')
            if not correct_answer:
                raise serializers.ValidationError("使用字符串选项格式时，必须提供correct或correct_answer字段")
        else:
            # 字典格式，统计正确答案数量
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
        # 统一字段名
        description = data.get('description') or data.get('question', '')
        
        # 确定题目类型
        question_type = data.get('question_type')
        if question_type is None:
            type_str = data.get('type', 'single')
            question_type = 0 if type_str == 'single' else 1
        
        # 处理选项
        options = data.get('options', [])
        correct_answer = data.get('correct_answer') or data.get('correct', '')
        
        # 获取编程语言
        language = data.get('language', '')
        
        # 处理题目描述中的代码块
        if language:
            description = process_html_with_language(description, language)
        
        # 处理解释中的代码块
        explanation = data.get('explanation', '')
        if explanation and language:
            explanation = process_html_with_language(explanation, language)
        
        # 转换选项格式
        converted_options = []
        if options and isinstance(options[0], str):
            # 字符串数组格式，需要转换为字典格式
            for i, option_text in enumerate(options):
                # 判断是否为正确答案
                is_correct = False
                if correct_answer:
                    # 支持多种正确答案格式：A, B, C, D 或 0, 1, 2, 3
                    if correct_answer.upper() == chr(65 + i):  # A, B, C, D
                        is_correct = True
                    elif correct_answer == str(i):  # 0, 1, 2, 3
                        is_correct = True
                    elif correct_answer == str(i + 1):  # 1, 2, 3, 4
                        is_correct = True
                
                converted_options.append({
                    'content': option_text,
                    'is_correct': is_correct
                })
        else:
            # 已经是字典格式
            converted_options = options
        
        # 处理选项格式，并处理选项中的代码块
        final_options = []
        for i, option in enumerate(converted_options):
            option_letter = chr(ord('A') + i)
            
            # 获取选项文本
            option_text = option.get('content', '')
            is_correct = option.get('is_correct', False)
            
            # 处理选项中的代码块
            if language:
                option_text = process_html_with_language(option_text, language)
            
            final_options.append({
                'key': option_letter,
                'text': option_text,
                'content': option_text,  # 同时提供content字段以兼容不同版本
                'is_correct': is_correct
            })
        
        # 转换题目类型 - 支持字符串和整数格式
        if isinstance(question_type, int):
            question_type_map = {0: 'single', 1: 'multiple'}
            question_type = question_type_map.get(question_type, 'single')
        # 如果已经是字符串格式，直接使用
        
        # 转换难度
        difficulty_map = {'Easy': 'easy', 'Mid': 'medium', 'Hard': 'hard'}
        difficulty = difficulty_map.get(data.get('difficulty', 'Easy'), 'easy')
        
        # 生成正确答案字符串
        correct_answers = []
        for i, option in enumerate(final_options):
            if option.get('is_correct', False):
                correct_answers.append(chr(ord('A') + i))
        
        # 如果没有正确答案，保持为空（不默认设为A）
        if not correct_answers:
            print(f"警告：题目 '{description}' 没有正确答案")
            correct_answer_str = ''
        else:
            correct_answer_str = ''.join(correct_answers)
        
        # 返回转换后的数据
        return {
            '_id': data.get('id', ''),
            'title': data.get('title') or data.get('question', ''),  # 支持title或question字段
            'description': description,
            'question_type': question_type,
            'difficulty': difficulty,
            'score': data.get('score', 2),
            'options': final_options,  # 保持为列表格式
            'correct_answer': correct_answer_str,
            'explanation': explanation,
            'visible': data.get('visible', True),
            'language': language,
            'import_order': 0  # 添加import_order字段
        }
        




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
                # 直接转换数据格式，因为question_data已经经过验证
                item_serializer = ChoiceQuestionImportItemSerializer()
                converted_data = item_serializer.convert_to_create_format(question_data)
                
                # 添加分类
                if category_id:
                    converted_data['category'] = category_id
                
                # 添加编程语言
                if language and not converted_data.get('language'):
                    converted_data['language'] = language
                
                # 生成显示ID
                if not converted_data.get('_id'):
                    import uuid
                    converted_data['_id'] = str(uuid.uuid4())[:8].upper()
                
                # 使用现有的创建序列化器
                serializer = ChoiceQuestionCreateSerializer(data=converted_data)
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