# -*- coding: utf-8 -*-
"""
试卷相关序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import (
    ExamPaper,
    ExamPaperQuestion,
    ExamSession,
    ChoiceQuestion,
    Category
)
from .base import (
    UserSerializer,
    ChoiceQuestionCategorySerializer,
    ChoiceQuestionListSerializer
)

User = get_user_model()


class ExamPaperListSerializer(serializers.ModelSerializer):
    """
    试卷列表序列化器
    """
    category = ChoiceQuestionCategorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    question_count_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamPaper
        fields = [
            'id', 'title', 'description', 'category', 'question_count',
            'score_per_question', 'total_score', 'time_limit',
            'difficulty_filter', 'question_type_filter', 'created_by',
            'is_active', 'is_public', 'create_time', 'question_count_display'
        ]
    
    def get_question_count_display(self, obj):
        """
        获取实际可用题目数量
        """
        return obj.paper_questions.count()


class ExamPaperDetailSerializer(serializers.ModelSerializer):
    """
    试卷详情序列化器
    """
    category = ChoiceQuestionCategorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamPaper
        fields = '__all__'
    
    def get_questions(self, obj):
        """
        获取试卷题目列表
        """
        paper_questions = obj.paper_questions.select_related('question').all()
        return ExamPaperQuestionSerializer(paper_questions, many=True).data


class ExamPaperCreateSerializer(serializers.ModelSerializer):
    """
    试卷创建序列化器
    """
    
    class Meta:
        model = ExamPaper
        exclude = ['created_by', 'create_time', 'last_update_time', 'total_score']
    
    def validate_question_count(self, value):
        """
        验证题目数量
        """
        if value < 1 or value > 100:
            raise serializers.ValidationError("题目数量必须在1-100之间")
        return value
    
    def validate_time_limit(self, value):
        """
        验证考试时长
        """
        if value < 1 or value > 300:
            raise serializers.ValidationError("考试时长必须在1-300分钟之间")
        return value
    
    def validate(self, attrs):
        """
        验证试卷配置
        """
        # 检查是否有足够的题目
        category = attrs.get('category')
        difficulty_filter = attrs.get('difficulty_filter', 'mixed')
        question_type_filter = attrs.get('question_type_filter', 'mixed')
        question_count = attrs.get('question_count', 10)
        
        queryset = ChoiceQuestion.objects.filter(
            visible=True,
            is_public=True
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if difficulty_filter != 'mixed':
            queryset = queryset.filter(difficulty=difficulty_filter)
        
        if question_type_filter != 'mixed':
            queryset = queryset.filter(question_type=question_type_filter)
        
        available_count = queryset.count()
        if available_count < question_count:
            raise serializers.ValidationError(
                f"可用题目数量不足，当前筛选条件下只有{available_count}道题目，需要{question_count}道题目"
            )
        
        return attrs


class ExamPaperQuestionSerializer(serializers.ModelSerializer):
    """
    试卷题目序列化器
    """
    question = ChoiceQuestionListSerializer(read_only=True)
    
    class Meta:
        model = ExamPaperQuestion
        fields = ['id', 'question', 'order', 'score']


class ExamSessionListSerializer(serializers.ModelSerializer):
    """
    考试会话列表序列化器
    """
    exam_paper = ExamPaperListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    accuracy_rate = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'exam_paper', 'user', 'status', 'start_time', 'end_time',
            'submit_time', 'total_score', 'max_score', 'correct_count',
            'total_count', 'accuracy_rate', 'duration', 'create_time'
        ]
    
    def get_accuracy_rate(self, obj):
        """
        获取正确率
        """
        return obj.get_accuracy_rate()
    
    def get_duration(self, obj):
        """
        获取考试时长（分钟）
        """
        if obj.start_time and obj.end_time:
            duration = (obj.end_time - obj.start_time).total_seconds() / 60
            return round(duration, 2)
        return 0


class ExamSessionDetailSerializer(serializers.ModelSerializer):
    """
    考试会话详情序列化器
    """
    exam_paper = ExamPaperDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    accuracy_rate = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamSession
        fields = '__all__'
    
    def get_accuracy_rate(self, obj):
        """
        获取正确率
        """
        return obj.get_accuracy_rate()
    
    def get_duration(self, obj):
        """
        获取考试时长（分钟）
        """
        if obj.start_time and obj.end_time:
            duration = (obj.end_time - obj.start_time).total_seconds() / 60
            return round(duration, 2)
        return 0
    
    def get_remaining_time(self, obj):
        """
        获取剩余时间（秒）
        """
        return obj.get_remaining_time()


class ExamSessionCreateSerializer(serializers.ModelSerializer):
    """
    考试会话创建序列化器
    """
    
    class Meta:
        model = ExamSession
        fields = ['exam_paper']
    
    def validate_exam_paper(self, value):
        """
        验证试卷
        """
        if not value.is_active:
            raise serializers.ValidationError("试卷已停用")
        
        if not value.is_public:
            raise serializers.ValidationError("试卷未公开")
        
        # 检查试卷是否有题目
        if value.paper_questions.count() == 0:
            raise serializers.ValidationError("试卷没有题目")
        
        return value


class ExamAnswerSerializer(serializers.Serializer):
    """
    考试答题序列化器
    """
    question_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=10)
    
    def validate_answer(self, value):
        """
        验证答案格式
        """
        if not value:
            raise serializers.ValidationError("答案不能为空")
        return value


class ExamSubmitSerializer(serializers.Serializer):
    """
    考试提交序列化器
    """
    answers = ExamAnswerSerializer(many=True)
    
    def validate_answers(self, value):
        """
        验证答案列表
        """
        if not value:
            raise serializers.ValidationError("答案列表不能为空")
        
        # 检查是否有重复的题目ID
        question_ids = [answer['question_id'] for answer in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("存在重复的题目ID")
        
        return value