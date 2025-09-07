# -*- coding: utf-8 -*-
"""
专题模型
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import PluginBaseModel
from .category import Category
from .tag import QuestionTag
from .question import ChoiceQuestion


class Topic(PluginBaseModel):
    """
    专题模型
    """
    
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
        (4, '专家'),
        (5, '大师'),
    ]
    
    title = models.CharField(
        max_length=200, 
        verbose_name="专题标题",
        help_text="专题的标题"
    )
    
    description = models.TextField(
        verbose_name="专题描述",
        help_text="专题的详细描述"
    )
    
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1,
        verbose_name="难度等级",
        help_text="专题的难度等级"
    )
    
    cover_image = models.URLField(
        blank=True,
        null=True,
        verbose_name="封面图片",
        help_text="专题封面图片URL"
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name="是否公开",
        help_text="是否对所有用户公开"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="是否启用此专题"
    )
    
    pass_score = models.IntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="及格分数",
        help_text="专题的及格分数（0-100）"
    )
    
    total_questions = models.IntegerField(
        default=0,
        verbose_name="题目总数",
        help_text="专题包含的题目总数"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="创建者",
        help_text="专题的创建者"
    )
    
    class Meta:
        db_table = "choice_question_topic"
        verbose_name = "专题"
        verbose_name_plural = "专题"
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return self.title
    
    def update_question_count(self):
        """
        更新题目总数
        """
        self.total_questions = self.topic_questions.count()
        self.save(update_fields=['total_questions'])
    
    def get_questions(self):
        """
        获取专题的所有题目（按顺序）
        """
        return ChoiceQuestion.objects.filter(
            topic_questions__topic=self
        ).order_by('topic_questions__order_index')
    
    def get_categories(self):
        """
        获取专题关联的分类
        """
        return Category.objects.filter(
            topic_categories__topic=self
        )
    
    def get_tags(self):
        """
        获取专题关联的标签
        """
        return QuestionTag.objects.filter(
            topic_tags__topic=self
        )


class TopicCategoryRelation(PluginBaseModel):
    """
    专题分类关联表
    """
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='topic_categories',
        verbose_name="专题"
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='topic_categories',
        verbose_name="分类"
    )
    
    class Meta:
        db_table = "choice_question_topic_category"
        verbose_name = "专题分类关联"
        verbose_name_plural = "专题分类关联"
        unique_together = ['topic', 'category']
        indexes = [
            models.Index(fields=['topic']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.topic.title} - {self.category.name}"


class TopicTagRelation(PluginBaseModel):
    """
    专题标签关联表
    """
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='topic_tags',
        verbose_name="专题"
    )
    
    tag = models.ForeignKey(
        QuestionTag,
        on_delete=models.CASCADE,
        related_name='topic_tags',
        verbose_name="标签"
    )
    
    class Meta:
        db_table = "choice_question_topic_tag"
        verbose_name = "专题标签关联"
        verbose_name_plural = "专题标签关联"
        unique_together = ['topic', 'tag']
        indexes = [
            models.Index(fields=['topic']),
            models.Index(fields=['tag']),
        ]
    
    def __str__(self):
        return f"{self.topic.title} - {self.tag.name}"


class TopicQuestion(PluginBaseModel):
    """
    专题题目关联表
    """
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='topic_questions',
        verbose_name="专题"
    )
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name='topic_questions',
        verbose_name="题目"
    )
    
    order_index = models.IntegerField(
        default=0,
        verbose_name="排序索引",
        help_text="题目在专题中的排序"
    )
    
    class Meta:
        db_table = "choice_question_topic_question"
        verbose_name = "专题题目关联"
        verbose_name_plural = "专题题目关联"
        unique_together = ['topic', 'question']
        ordering = ['order_index']
        indexes = [
            models.Index(fields=['topic', 'order_index']),
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"{self.topic.title} - {self.question.title}"


class TopicPracticeRecord(PluginBaseModel):
    """
    专题练习记录
    """
    
    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('paused', '已暂停'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="用户",
        help_text="练习的用户"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        verbose_name="专题",
        help_text="练习的专题"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name="练习状态"
    )
    
    total_questions = models.IntegerField(
        default=0,
        verbose_name="题目总数"
    )
    
    answered_questions = models.IntegerField(
        default=0,
        verbose_name="已答题数"
    )
    
    correct_answers = models.IntegerField(
        default=0,
        verbose_name="正确答案数"
    )
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="得分"
    )
    
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="开始时间"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="结束时间"
    )
    
    time_spent = models.IntegerField(
        default=0,
        verbose_name="用时（秒）"
    )
    
    class Meta:
        db_table = "choice_question_topic_practice"
        verbose_name = "专题练习记录"
        verbose_name_plural = "专题练习记录"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'topic']),
            models.Index(fields=['status']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.title}"
    
    def calculate_score(self):
        """
        计算得分
        """
        if self.total_questions > 0:
            self.score = (self.correct_answers / self.total_questions) * 100
        else:
            self.score = 0
        return self.score
    
    def is_passed(self):
        """
        是否及格
        """
        return self.score >= self.topic.pass_score


class TopicWrongQuestionRecord(PluginBaseModel):
    """
    专题错题记录
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="用户"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        verbose_name="专题"
    )
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name="题目"
    )
    
    practice_record = models.ForeignKey(
        TopicPracticeRecord,
        on_delete=models.CASCADE,
        verbose_name="练习记录"
    )
    
    user_answer = models.CharField(
        max_length=10,
        verbose_name="用户答案"
    )
    
    correct_answer = models.CharField(
        max_length=10,
        verbose_name="正确答案"
    )
    
    is_reviewed = models.BooleanField(
        default=False,
        verbose_name="是否已复习"
    )
    
    review_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="复习时间"
    )
    
    class Meta:
        db_table = "choice_question_topic_wrong"
        verbose_name = "专题错题记录"
        verbose_name_plural = "专题错题记录"
        ordering = ['-create_time']
        unique_together = ['user', 'topic', 'question', 'practice_record']
        indexes = [
            models.Index(fields=['user', 'topic']),
            models.Index(fields=['question']),
            models.Index(fields=['is_reviewed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.title} - {self.question.title}"
    
    def mark_reviewed(self):
        """
        标记为已复习
        """
        from django.utils import timezone
        self.is_reviewed = True
        self.review_time = timezone.now()
        self.save(update_fields=['is_reviewed', 'review_time'])