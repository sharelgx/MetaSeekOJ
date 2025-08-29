from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category,
    QuestionTag,
    ChoiceQuestion,
    ChoiceQuestionSubmission,
    WrongQuestion
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ChoiceQuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ChoiceQuestionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionTag
        fields = '__all__'


class ChoiceQuestionListSerializer(serializers.ModelSerializer):
    """选择题列表序列化器"""
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = ChoiceQuestionTagSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ChoiceQuestion
        fields = [
            'id', '_id', 'title', 'question_type', 'difficulty', 'score',
            'category', 'tags', 'created_by', 'create_time', 'last_update_time',
            'total_submit', 'total_accepted', 'acceptance_rate'
        ]


class ChoiceQuestionDetailSerializer(serializers.ModelSerializer):
    """选择题详情序列化器"""
    category = ChoiceQuestionCategorySerializer(read_only=True)
    tags = ChoiceQuestionTagSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ChoiceQuestion
        fields = '__all__'


class ChoiceQuestionCreateSerializer(serializers.ModelSerializer):
    """选择题创建序列化器"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=QuestionTag.objects.all(),
        required=False
    )
    
    class Meta:
        model = ChoiceQuestion
        exclude = ['_id', 'create_time', 'last_update_time', 'created_by',
                  'total_submit', 'total_accepted']
        
    def validate_options(self, value):
        """验证选项格式"""
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError("至少需要2个选项")
        
        for option in value:
            if not isinstance(option, dict) or 'key' not in option or 'value' not in option:
                raise serializers.ValidationError("选项格式错误")
        
        return value
    
    def validate_correct_answer(self, value):
        """验证正确答案格式"""
        if not value:
            raise serializers.ValidationError("必须指定正确答案")
        return value


class ChoiceQuestionSubmissionSerializer(serializers.ModelSerializer):
    """选择题提交记录序列化器"""
    user = UserSerializer(read_only=True)
    question = ChoiceQuestionListSerializer(read_only=True)
    
    class Meta:
        model = ChoiceQuestionSubmission
        fields = '__all__'


class ChoiceQuestionSubmissionCreateSerializer(serializers.ModelSerializer):
    """选择题提交创建序列化器"""
    class Meta:
        model = ChoiceQuestionSubmission
        fields = ['question', 'selected_answer']
        
    def validate_selected_answer(self, value):
        """验证用户答案格式"""
        if not value:
            raise serializers.ValidationError("必须提供答案")
        return value


class WrongQuestionSerializer(serializers.ModelSerializer):
    """错题本序列化器"""
    user = UserSerializer(read_only=True)
    question = ChoiceQuestionListSerializer(read_only=True)
    
    class Meta:
        model = WrongQuestion
        fields = '__all__'