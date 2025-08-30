from rest_framework import serializers
import json
from ..models.question import ChoiceQuestion


class ChoiceQuestionCreateSerializer(serializers.ModelSerializer):
    """
    创建选择题的序列化器 - 处理所有数据格式转换
    """
    options = serializers.JSONField()
    tags = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    question_type = serializers.CharField(default='single')
    difficulty = serializers.CharField()
    
    class Meta:
        model = ChoiceQuestion
        fields = '__all__'
    
    def validate_difficulty(self, value):
        """
        验证并转换难度值 - 支持多种输入格式
        """
        # 支持的难度值映射
        difficulty_map = {
            # 英文格式（前端可能发送的）
            'Easy': 'easy',
            'Medium': 'medium', 
            'Hard': 'hard',
            'easy': 'easy',
            'medium': 'medium',
            'hard': 'hard',
            # 中文格式
            '简单': 'easy',
            '中等': 'medium',
            '困难': 'hard',
            # 数字格式（兼容旧版本）
            '1': 'easy',
            '2': 'medium',
            '3': 'hard',
            1: 'easy',
            2: 'medium', 
            3: 'hard'
        }
        
        if value in difficulty_map:
            return difficulty_map[value]
            
        # 如果已经是正确格式，直接返回
        if value in ['easy', 'medium', 'hard']:
            return value
            
        raise serializers.ValidationError(f"无效的难度值: {value}，支持的值: easy, medium, hard")
    
    def validate_question_type(self, value):
        """
        验证并转换题目类型
        """
        type_map = {
            'single_choice': 'single',
            'multiple_choice': 'multiple', 
            'single': 'single',
            'multiple': 'multiple',
            '单选题': 'single',
            '多选题': 'multiple'
        }
        
        if value in type_map:
            return type_map[value]
            
        # 如果已经是正确格式，直接返回
        if value in ['single', 'multiple']:
            return value
            
        raise serializers.ValidationError(f"无效的题目类型: {value}，支持的值: single, multiple")
    
    def validate_options(self, value):
        """
        验证选项格式 - 支持多种输入格式
        """
        # 如果是字符串，尝试解析为JSON
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("选项格式错误，必须是有效的JSON格式")
        
        if not isinstance(value, list):
            raise serializers.ValidationError("选项必须是数组格式")
        
        if len(value) < 2:
            raise serializers.ValidationError("至少需要2个选项")
        
        # 验证每个选项的格式
        for i, option in enumerate(value):
            if not isinstance(option, dict):
                raise serializers.ValidationError(f"选项 {i+1} 格式错误，必须是对象格式")
            
            # 支持多种选项格式
            if 'key' not in option and 'value' not in option and 'id' not in option:
                raise serializers.ValidationError(f"选项 {i+1} 必须包含 key、value 或 id 字段")
            
            if 'text' not in option and 'content' not in option and 'label' not in option:
                raise serializers.ValidationError(f"选项 {i+1} 必须包含 text、content 或 label 字段")
        
        return value
    
    def validate_correct_answer(self, value):
        """
        验证正确答案格式
        """
        if not value:
            raise serializers.ValidationError("正确答案不能为空")
        
        return value


class ChoiceQuestionEditSerializer(serializers.ModelSerializer):
    """
    编辑选择题的序列化器
    """
    options = serializers.JSONField()
    tags = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    difficulty = serializers.CharField(required=False)
    question_type = serializers.CharField(required=False)
    
    class Meta:
        model = ChoiceQuestion
        fields = '__all__'
    
    def validate_difficulty(self, value):
        """复用创建序列化器的验证逻辑"""
        return ChoiceQuestionCreateSerializer().validate_difficulty(value)
    
    def validate_question_type(self, value):
        """复用创建序列化器的验证逻辑"""
        return ChoiceQuestionCreateSerializer().validate_question_type(value)
    
    def validate_options(self, value):
        """复用创建序列化器的验证逻辑"""
        return ChoiceQuestionCreateSerializer().validate_options(value)


class ChoiceQuestionListSerializer(serializers.ModelSerializer):
    """
    选择题列表序列化器
    """
    
    class Meta:
        model = ChoiceQuestion
        fields = '__all__'


class ChoiceQuestionDetailSerializer(serializers.ModelSerializer):
    """
    选择题详情序列化器
    """
    
    class Meta:
        model = ChoiceQuestion
        fields = '__all__'


# 为了兼容现有代码，保留原有的序列化器名称
ChoiceQuestionSerializer = ChoiceQuestionDetailSerializer
QuestionListSerializer = ChoiceQuestionListSerializer


class ChoiceQuestionSubmissionSerializer(serializers.Serializer):
    """
    选择题提交序列化器
    """
    selected_answer = serializers.CharField()
    time_spent = serializers.IntegerField(default=0)