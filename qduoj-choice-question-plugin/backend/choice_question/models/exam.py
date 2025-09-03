# -*- coding: utf-8 -*-
"""
试卷相关模型
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from account.models import User
from utils.models import JSONField
from .base import PluginBaseModel
from .question import ChoiceQuestion
from .category import Category


class ExamPaper(PluginBaseModel):
    """
    试卷模型
    """
    
    # 基本信息
    title = models.CharField(
        max_length=200,
        verbose_name="试卷标题"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="试卷描述"
    )
    
    # 试卷配置
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="所属分类"
    )
    
    # 题目配置
    question_count = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="题目数量"
    )
    
    score_per_question = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="每题分值"
    )
    
    total_score = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        verbose_name="总分"
    )
    
    # 时间配置
    time_limit = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        verbose_name="考试时长（分钟）"
    )
    
    # 难度筛选
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
        ('mixed', '混合'),
    ]
    
    difficulty_filter = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='mixed',
        verbose_name="难度筛选"
    )
    
    # 题型筛选
    TYPE_CHOICES = [
        ('single', '仅单选题'),
        ('multiple', '仅多选题'),
        ('mixed', '混合题型'),
    ]
    
    question_type_filter = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='mixed',
        verbose_name="题型筛选"
    )
    
    # 创建者和状态
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_exam_papers",
        verbose_name="创建者"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用"
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name="是否公开"
    )
    
    class Meta:
        db_table = "choice_plugin_exam_paper"
        verbose_name = "试卷"
        verbose_name_plural = "试卷"
        ordering = ['-create_time']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        重写save方法，自动计算总分
        """
        self.total_score = self.question_count * self.score_per_question
        super().save(*args, **kwargs)
    
    def generate_questions(self):
        """
        根据配置生成试卷题目
        """
        queryset = ChoiceQuestion.objects.filter(
            visible=True,
            is_public=True
        )
        
        # 按分类筛选
        if self.category:
            queryset = queryset.filter(category=self.category)
        
        # 按难度筛选
        if self.difficulty_filter != 'mixed':
            queryset = queryset.filter(difficulty=self.difficulty_filter)
        
        # 按题型筛选
        if self.question_type_filter != 'mixed':
            queryset = queryset.filter(question_type=self.question_type_filter)
        
        # 随机选择题目
        questions = queryset.order_by('?')[:self.question_count]
        
        # 清除现有题目关联
        ExamPaperQuestion.objects.filter(exam_paper=self).delete()
        
        # 创建新的题目关联
        for index, question in enumerate(questions, 1):
            ExamPaperQuestion.objects.create(
                exam_paper=self,
                question=question,
                order=index,
                score=self.score_per_question
            )
        
        return questions


class ExamPaperQuestion(PluginBaseModel):
    """
    试卷题目关联模型
    """
    
    exam_paper = models.ForeignKey(
        ExamPaper,
        on_delete=models.CASCADE,
        related_name="paper_questions",
        verbose_name="试卷"
    )
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name="题目"
    )
    
    order = models.IntegerField(
        verbose_name="题目顺序"
    )
    
    score = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        verbose_name="题目分值"
    )
    
    class Meta:
        db_table = "choice_plugin_exam_paper_question"
        verbose_name = "试卷题目"
        verbose_name_plural = "试卷题目"
        ordering = ['order']
        unique_together = [['exam_paper', 'question'], ['exam_paper', 'order']]
        
    def __str__(self):
        return f"{self.exam_paper.title} - 第{self.order}题"


class ExamSession(PluginBaseModel):
    """
    考试会话模型
    """
    
    # 基本信息
    exam_paper = models.ForeignKey(
        ExamPaper,
        on_delete=models.CASCADE,
        verbose_name="试卷"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="考试用户"
    )
    
    # 考试状态
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('submitted', '已提交'),
        ('timeout', '超时'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name="考试状态"
    )
    
    # 时间记录
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="开始时间"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="结束时间"
    )
    
    submit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="提交时间"
    )
    
    # 分数记录
    total_score = models.IntegerField(
        default=0,
        verbose_name="总得分"
    )
    
    max_score = models.IntegerField(
        default=0,
        verbose_name="满分"
    )
    
    correct_count = models.IntegerField(
        default=0,
        verbose_name="正确题数"
    )
    
    total_count = models.IntegerField(
        default=0,
        verbose_name="总题数"
    )
    
    # 答题记录
    answers = JSONField(
        default=dict,
        verbose_name="答题记录",
        help_text="格式: {question_id: {answer: 'A', is_correct: true, score: 2}}"
    )
    
    # 其他信息
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP地址"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="用户代理"
    )
    
    class Meta:
        db_table = "choice_plugin_exam_session"
        verbose_name = "考试会话"
        verbose_name_plural = "考试会话"
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['exam_paper', 'status']),
            models.Index(fields=['start_time']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.exam_paper.title}"
    
    def start_exam(self):
        """
        开始考试
        """
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.start_time = timezone.now()
            self.max_score = self.exam_paper.total_score
            self.total_count = self.exam_paper.question_count
            self.save()
    
    def submit_exam(self):
        """
        提交考试
        """
        if self.status == 'in_progress':
            self.status = 'submitted'
            self.submit_time = timezone.now()
            self.end_time = self.submit_time
            self._calculate_score()
            self.save()
    
    def check_timeout(self):
        """
        检查是否超时
        """
        if self.status == 'in_progress' and self.start_time:
            time_limit_seconds = self.exam_paper.time_limit * 60
            elapsed_time = (timezone.now() - self.start_time).total_seconds()
            
            if elapsed_time >= time_limit_seconds:
                self.status = 'timeout'
                self.end_time = timezone.now()
                self._calculate_score()
                self.save()
                return True
        return False
    
    def _calculate_score(self):
        """
        计算考试分数
        """
        total_score = 0
        correct_count = 0
        
        for question_id, answer_data in self.answers.items():
            if answer_data.get('is_correct', False):
                total_score += answer_data.get('score', 0)
                correct_count += 1
        
        self.total_score = total_score
        self.correct_count = correct_count
    
    def get_remaining_time(self):
        """
        获取剩余时间（秒）
        """
        if self.status != 'in_progress' or not self.start_time:
            return 0
        
        time_limit_seconds = self.exam_paper.time_limit * 60
        elapsed_time = (timezone.now() - self.start_time).total_seconds()
        remaining_time = max(0, time_limit_seconds - elapsed_time)
        
        return int(remaining_time)
    
    def get_accuracy_rate(self):
        """
        获取正确率
        """
        if self.total_count == 0:
            return 0
        return round((self.correct_count / self.total_count) * 100, 2)