# -*- coding: utf-8 -*-
"""
错题本模型
"""

from django.db import models
from django.core.validators import MinValueValidator
from account.models import User
from .base import PluginBaseModel
from .question import ChoiceQuestion


class WrongQuestion(PluginBaseModel):
    """
    错题本模型
    记录用户的错题信息
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="用户"
    )
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name="错题"
    )
    
    wrong_count = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="错误次数",
        help_text="用户答错此题的总次数"
    )
    
    last_wrong_time = models.DateTimeField(
        auto_now=True,
        verbose_name="最后错误时间"
    )
    
    first_wrong_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="首次错误时间"
    )
    
    note = models.TextField(
        blank=True,
        verbose_name="用户笔记",
        help_text="用户对此错题的个人笔记"
    )
    
    is_mastered = models.BooleanField(
        default=False,
        verbose_name="是否已掌握",
        help_text="用户是否已经掌握此题"
    )
    
    mastered_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="掌握时间"
    )
    
    # 错误类型分析
    ERROR_TYPE_CHOICES = [
        ('careless', '粗心错误'),
        ('knowledge', '知识点不熟'),
        ('comprehension', '理解错误'),
        ('calculation', '计算错误'),
        ('other', '其他'),
    ]
    
    error_type = models.CharField(
        max_length=20,
        choices=ERROR_TYPE_CHOICES,
        default='other',
        verbose_name="错误类型"
    )
    
    # 最后一次错误的答案
    last_wrong_answer = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="最后错误答案"
    )
    
    class Meta:
        db_table = "choice_question_wrong"
        verbose_name = "错题记录"
        verbose_name_plural = "错题记录"
        unique_together = ['user', 'question']
        ordering = ['-last_wrong_time']
        indexes = [
            models.Index(fields=['user', 'is_mastered']),
            models.Index(fields=['question', 'wrong_count']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.question.title[:30]} (错误{self.wrong_count}次)"
    
    def mark_as_mastered(self):
        """
        标记为已掌握
        """
        from django.utils import timezone
        self.is_mastered = True
        self.mastered_time = timezone.now()
        self.save(update_fields=['is_mastered', 'mastered_time'])
    
    def add_wrong_attempt(self, wrong_answer, error_type='other'):
        """
        增加错误尝试次数
        """
        from django.utils import timezone
        self.wrong_count += 1
        self.last_wrong_time = timezone.now()
        self.last_wrong_answer = wrong_answer
        self.error_type = error_type
        self.is_mastered = False  # 重新答错，标记为未掌握
        self.mastered_time = None
        self.save()
    
    @classmethod
    def add_or_update_wrong_question(cls, user, question, wrong_answer, error_type='other'):
        """
        添加或更新错题记录
        """
        wrong_question, created = cls.objects.get_or_create(
            user=user,
            question=question,
            defaults={
                'wrong_count': 1,
                'last_wrong_answer': wrong_answer,
                'error_type': error_type
            }
        )
        
        if not created:
            wrong_question.add_wrong_attempt(wrong_answer, error_type)
        
        return wrong_question
    
    @classmethod
    def get_user_wrong_questions(cls, user, is_mastered=None, category=None, difficulty=None):
        """
        获取用户的错题列表
        """
        queryset = cls.objects.filter(user=user)
        
        if is_mastered is not None:
            queryset = queryset.filter(is_mastered=is_mastered)
        
        if category:
            queryset = queryset.filter(question__category=category)
        
        if difficulty:
            queryset = queryset.filter(question__difficulty=difficulty)
        
        return queryset.select_related('question', 'question__category')
    
    @classmethod
    def get_user_statistics(cls, user):
        """
        获取用户错题统计
        """
        wrong_questions = cls.objects.filter(user=user)
        total_count = wrong_questions.count()
        mastered_count = wrong_questions.filter(is_mastered=True).count()
        
        # 按难度统计
        difficulty_stats = {}
        for difficulty in ['easy', 'medium', 'hard']:
            count = wrong_questions.filter(question__difficulty=difficulty).count()
            difficulty_stats[difficulty] = count
        
        # 按错误类型统计
        error_type_stats = {}
        for error_type, _ in cls.ERROR_TYPE_CHOICES:
            count = wrong_questions.filter(error_type=error_type).count()
            error_type_stats[error_type] = count
        
        return {
            'total_wrong_questions': total_count,
            'mastered_questions': mastered_count,
            'unmastered_questions': total_count - mastered_count,
            'mastery_rate': round((mastered_count / total_count) * 100, 2) if total_count > 0 else 0,
            'difficulty_statistics': difficulty_stats,
            'error_type_statistics': error_type_stats
        }
    
    @classmethod
    def get_review_questions(cls, user, limit=10):
        """
        获取需要复习的错题（优先级：错误次数多、最近错误、未掌握）
        """
        return cls.objects.filter(
            user=user,
            is_mastered=False
        ).order_by('-wrong_count', '-last_wrong_time')[:limit]