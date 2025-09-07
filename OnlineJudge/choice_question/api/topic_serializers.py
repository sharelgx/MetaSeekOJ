from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import (
    Topic, TopicCategoryRelation, TopicTagRelation, TopicQuestion,
    TopicPracticeRecord, TopicWrongQuestionRecord,
    Category, QuestionTag, ChoiceQuestion
)
from .serializers import ChoiceQuestionListSerializer

User = get_user_model()


class TopicCategorySerializer(serializers.ModelSerializer):
    """专题分类序列化器"""
    full_name = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'order', 'is_active', 
                 'full_name', 'level', 'question_count', 'create_time']
        read_only_fields = ['create_time']


class TopicCategoryDetailSerializer(serializers.ModelSerializer):
    """专题分类详情序列化器"""
    full_name = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'parent_name', 'order', 
                 'is_active', 'full_name', 'level', 'question_count', 'children_count',
                 'topic_count', 'create_time', 'update_time']
        read_only_fields = ['create_time', 'update_time']
    
    def get_children_count(self, obj):
        """获取子分类数量"""
        return obj.get_children().count()
    
    def get_topic_count(self, obj):
        """获取关联专题数量"""
        from ..models import TopicCategoryRelation
        return TopicCategoryRelation.objects.filter(category=obj).count()


class TopicTagSerializer(serializers.ModelSerializer):
    """专题标签序列化器"""
    class Meta:
        model = QuestionTag
        fields = ['id', 'name', 'color', 'description']


class TopicQuestionSerializer(serializers.ModelSerializer):
    """专题题目序列化器"""
    question = ChoiceQuestionListSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TopicQuestion
        fields = ['id', 'question', 'question_id', 'order_index']


class TopicListSerializer(serializers.ModelSerializer):
    """专题列表序列化器"""
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    question_count = serializers.SerializerMethodField()
    practice_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'description', 'difficulty_level',
            'is_active', 'is_public', 'created_by_name', 'create_time', 'update_time',
            'categories', 'tags', 'question_count', 'practice_count'
        ]
    
    def get_categories(self, obj):
        """获取专题分类"""
        relations = TopicCategoryRelation.objects.filter(topic=obj).select_related('category')
        return [{
            'id': rel.category.id,
            'name': rel.category.name,
            'description': rel.category.description
        } for rel in relations]
    
    def get_tags(self, obj):
        """获取专题标签"""
        relations = TopicTagRelation.objects.filter(topic=obj).select_related('tag')
        return [{
            'id': rel.tag.id,
            'name': rel.tag.name,
            'color': rel.tag.color
        } for rel in relations]
    
    def get_question_count(self, obj):
        """获取题目数量"""
        return TopicQuestion.objects.filter(topic=obj).count()
    
    def get_practice_count(self, obj):
        """获取练习次数"""
        return TopicPracticeRecord.objects.filter(topic=obj).count()


class TopicDetailSerializer(serializers.ModelSerializer):
    """专题详情序列化器"""
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'description', 'difficulty_level',
            'is_active', 'is_public', 'created_by', 'created_by_name', 
            'create_time', 'update_time', 'categories', 'tags', 
            'questions', 'statistics'
        ]
    
    def get_categories(self, obj):
        """获取专题分类"""
        relations = TopicCategoryRelation.objects.filter(topic=obj).select_related('category')
        return [{
            'id': rel.category.id,
            'name': rel.category.name,
            'description': rel.category.description
        } for rel in relations]
    
    def get_tags(self, obj):
        """获取专题标签"""
        relations = TopicTagRelation.objects.filter(topic=obj).select_related('tag')
        return [{
            'id': rel.tag.id,
            'name': rel.tag.name,
            'color': rel.tag.color
        } for rel in relations]
    
    def get_questions(self, obj):
        """获取专题题目"""
        topic_questions = TopicQuestion.objects.filter(
            topic=obj
        ).select_related('question').order_by('order_index')
        
        return [{
            'id': tq.id,
            'order': tq.order_index,
            'question': {
                'id': tq.question.id,
                'title': tq.question.title,
                'difficulty': tq.question.difficulty,
                'score': tq.question.score,
                'question_type': tq.question.question_type
            }
        } for tq in topic_questions]
    
    def get_statistics(self, obj):
        """获取专题统计信息"""
        total_practices = TopicPracticeRecord.objects.filter(topic=obj).count()
        completed_practices = TopicPracticeRecord.objects.filter(
            topic=obj, status='completed'
        ).count()
        
        return {
            'total_practices': total_practices,
            'completed_practices': completed_practices,
            'completion_rate': round(completed_practices / total_practices * 100, 2) if total_practices > 0 else 0
        }


class TopicCreateSerializer(serializers.ModelSerializer):
    """专题创建序列化器"""
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Topic
        fields = [
            'title', 'description', 'difficulty_level',
            'is_active', 'is_public', 'category_ids', 'tag_ids', 'question_ids'
        ]
    
    def create(self, validated_data):
        """创建专题"""
        category_ids = validated_data.pop('category_ids', [])
        tag_ids = validated_data.pop('tag_ids', [])
        question_ids = validated_data.pop('question_ids', [])
        
        # 设置创建者
        validated_data['created_by'] = self.context['request'].user
        
        # 创建专题
        topic = Topic.objects.create(**validated_data)
        
        # 创建分类关联
        for category_id in category_ids:
            try:
                TopicCategoryRelation.objects.create(
                    topic=topic,
                    category_id=category_id
                )
            except Exception as e:
                print(f'创建分类关联失败: {e}')
        
        # 创建标签关联
        for tag_id in tag_ids:
            try:
                TopicTagRelation.objects.create(
                    topic=topic,
                    tag_id=tag_id
                )
            except Exception as e:
                print(f'创建标签关联失败: {e}')
        
        # 创建题目关联
        for index, question_id in enumerate(question_ids):
            try:
                TopicQuestion.objects.create(
                    topic=topic,
                    question_id=question_id,
                    order_index=index + 1
                )
            except Exception as e:
                print(f'创建题目关联失败: {e}')
        
        # 更新题目总数
        topic.total_questions = len(question_ids)
        topic.save()
        
        return topic


class TopicUpdateSerializer(serializers.ModelSerializer):
    """专题更新序列化器"""
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Topic
        fields = [
            'title', 'description', 'difficulty_level',
            'is_active', 'is_public', 'category_ids', 'tag_ids', 'question_ids'
        ]
    
    def update(self, instance, validated_data):
        """更新专题"""
        category_ids = validated_data.pop('category_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)
        question_ids = validated_data.pop('question_ids', None)
        
        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新分类关联
        if category_ids is not None:
            TopicCategoryRelation.objects.filter(topic=instance).delete()
            for category_id in category_ids:
                TopicCategoryRelation.objects.create(
                    topic=instance,
                    category_id=category_id
                )
        
        # 更新标签关联
        if tag_ids is not None:
            TopicTagRelation.objects.filter(topic=instance).delete()
            for tag_id in tag_ids:
                TopicTagRelation.objects.create(
                    topic=instance,
                    tag_id=tag_id
                )
        
        # 更新题目关联
        if question_ids is not None:
            TopicQuestion.objects.filter(topic=instance).delete()
            for index, question_id in enumerate(question_ids):
                TopicQuestion.objects.create(
                    topic=instance,
                    question_id=question_id,
                    order_index=index + 1
                )
        
        return instance


class TopicPracticeRecordSerializer(serializers.ModelSerializer):
    """专题练习记录序列化器"""
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TopicPracticeRecord
        fields = [
            'id', 'topic', 'topic_title', 'user', 'user_name', 'status',
            'start_time', 'end_time', 'total_questions', 'answered_questions',
            'correct_answers', 'score', 'time_spent'
        ]
        read_only_fields = ['user', 'start_time']


class TopicPracticeSubmitSerializer(serializers.Serializer):
    """专题练习提交序列化器"""
    topic_id = serializers.IntegerField()
    answers = serializers.JSONField()
    time_spent = serializers.IntegerField(default=0)
    
    def validate_topic_id(self, value):
        """验证专题ID"""
        try:
            topic = Topic.objects.get(id=value, is_active=True)
            return value
        except Topic.DoesNotExist:
            raise serializers.ValidationError("专题不存在或已禁用")
    
    def validate_answers(self, value):
        """验证答案格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("答案格式错误")
        return value


class TopicWrongQuestionRecordSerializer(serializers.ModelSerializer):
    """专题错题记录序列化器"""
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    question_title = serializers.CharField(source='question.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TopicWrongQuestionRecord
        fields = [
            'id', 'topic', 'topic_title', 'question', 'question_title',
            'user', 'user_name', 'user_answer', 'correct_answer',
            'is_reviewed', 'review_time', 'create_time'
        ]
        read_only_fields = ['user', 'create_time']


class WrongQuestionStatisticsSerializer(serializers.Serializer):
    """错题统计序列化器"""
    total_wrong = serializers.IntegerField()
    reviewed_count = serializers.IntegerField()
    unreviewed_count = serializers.IntegerField()
    review_rate = serializers.FloatField()
    topic_distribution = serializers.ListField()
    difficulty_distribution = serializers.ListField()
