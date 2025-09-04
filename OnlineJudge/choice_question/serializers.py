from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category,
    QuestionTag,
    ChoiceQuestion,
    ChoiceQuestionSubmission,
    WrongQuestion,
    ExamPaper,
    ExamSession
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
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ChoiceQuestion
        fields = [
            'id', '_id', 'title', 'question_type', 'difficulty', 'score',
            'category', 'tags', 'created_by', 'create_time', 'last_update_time',
            'total_submit', 'total_accepted', 'acceptance_rate'
        ]
    
    def get_category(self, obj):
        """获取分类信息"""
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name
            }
        return None
    
    def get_tags(self, obj):
        """获取标签信息"""
        return [
            {
                'id': tag.id,
                'name': tag.name,
                'color': getattr(tag, 'color', '#409EFF')
            }
            for tag in obj.tags.all()
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
    question_type = serializers.ChoiceField(
        choices=ChoiceQuestion.QUESTION_TYPE_CHOICES,
        default='single',
        required=False
    )
    difficulty = serializers.CharField(
        default='easy',
        required=False
    )
    
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
    
    class Meta:
        model = ChoiceQuestion
        exclude = ['_id', 'create_time', 'last_update_time', 'created_by',
                  'total_submit', 'total_accepted', 'tags']
        
    def validate_options(self, value):
        """验证选项格式"""
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError("至少需要2个选项")
        
        for option in value:
            if not isinstance(option, dict):
                raise serializers.ValidationError("选项格式错误：每个选项必须是字典格式")
            
            # 支持两种格式：前端格式 {content, is_correct, explanation} 和后端格式 {key, text}
            if 'content' not in option and 'key' not in option and 'text' not in option:
                raise serializers.ValidationError("选项格式错误：缺少必要的内容字段")
            
            # 检查内容是否为空
            content = option.get('content') or option.get('text') or option.get('value', '')
            if not content or not content.strip():
                raise serializers.ValidationError("选项内容不能为空")
        
        return value
    
    def validate_correct_answer(self, value):
        """验证正确答案格式"""
        if not value:
            raise serializers.ValidationError("必须指定正确答案")
        return value
    
    def validate(self, attrs):
        """整体验证并转换数据格式"""
        # 转换前端选项格式到后端格式
        if 'options' in attrs:
            converted_options = []
            correct_answers = []
            
            for i, option in enumerate(attrs['options']):
                # 生成选项键（A, B, C, D...）
                option_key = chr(65 + i)
                
                # 转换格式
                if 'content' in option:
                    # 前端格式：{content, is_correct, explanation}
                    converted_option = {
                        'key': option_key,
                        'text': option['content']
                    }
                    if option.get('is_correct'):
                        correct_answers.append(option_key)
                else:
                    # 后端格式：{key, text} 或 {key, value}
                    converted_option = {
                        'key': option.get('key', option_key),
                        'text': option.get('text') or option.get('value', '')
                    }
                
                converted_options.append(converted_option)
            
            attrs['options'] = converted_options
            
            # 如果没有指定正确答案，从选项中提取
            if not attrs.get('correct_answer') and correct_answers:
                attrs['correct_answer'] = ','.join(correct_answers) if len(correct_answers) > 1 else correct_answers[0]
        
        return attrs


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
        fields = ['question', 'user', 'selected_answer', 'is_correct', 'score', 'time_spent', 'ip_address', 'user_agent']
        
    def validate_selected_answer(self, value):
        """验证用户答案格式"""
        if not value:
            raise serializers.ValidationError("必须提供答案")
        return value


class WrongQuestionSerializer(serializers.ModelSerializer):
    """错题序列化器"""
    user = UserSerializer(read_only=True)
    question = ChoiceQuestionListSerializer(read_only=True)
    
    class Meta:
        model = WrongQuestion
        fields = '__all__'


class ExamPaperSerializer(serializers.ModelSerializer):
    """试卷序列化器"""
    created_by = UserSerializer(read_only=True)
    categories = ChoiceQuestionCategorySerializer(many=True, read_only=True)
    tags = ChoiceQuestionTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExamPaper
        fields = '__all__'


class ExamSessionSerializer(serializers.ModelSerializer):
    """考试会话序列化器"""
    user = UserSerializer(read_only=True)
    paper = ExamPaperSerializer(read_only=True)
    score_percentage = serializers.SerializerMethodField()
    accuracy_rate = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()
    exam_paper_title = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamSession
        fields = '__all__'
    
    def get_score_percentage(self, obj):
        """计算得分率"""
        if obj.paper and obj.paper.total_score > 0:
            return round((obj.score or 0) / obj.paper.total_score * 100, 1)
        return 0
    
    def get_accuracy_rate(self, obj):
        """计算正确率"""
        if obj.total_count > 0:
            return round((obj.correct_count or 0) / obj.total_count * 100, 1)
        return 0
    
    def get_duration(self, obj):
        """计算考试用时（分钟）"""
        if obj.start_time and obj.end_time:
            duration_seconds = (obj.end_time - obj.start_time).total_seconds()
            return int(duration_seconds / 60)
        return 0
    
    def get_max_score(self, obj):
        """获取满分"""
        return obj.paper.total_score if obj.paper else 0
    
    def get_exam_paper_title(self, obj):
        """获取试卷标题"""
        return obj.paper.title if obj.paper else ''