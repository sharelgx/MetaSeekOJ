# -*- coding: utf-8 -*-
"""
选择题模型
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.models import JSONField, RichTextField
from account.models import User
from .base import PluginBaseModel
from .category import Category
from .tag import QuestionTag


class ChoiceQuestion(PluginBaseModel):
    """
    选择题模型
    """
    
    # 基本信息
    _id = models.CharField(
        max_length=32, 
        db_index=True, 
        verbose_name="显示ID",
        help_text="题目的显示ID，用于前端展示"
    )
    
    title = models.TextField(
        verbose_name="题目标题",
        help_text="题目的标题或问题描述"
    )
    
    description = RichTextField(
        verbose_name="题目描述",
        help_text="题目的详细描述，支持富文本格式"
    )
    
    # 题目类型
    QUESTION_TYPE_CHOICES = [
        ('single', '单选题'),
        ('multiple', '多选题'),
    ]
    
    question_type = models.CharField(
        max_length=10, 
        choices=QUESTION_TYPE_CHOICES,
        verbose_name="题目类型"
    )
    
    # 选项和答案
    options = JSONField(
        verbose_name="选项列表",
        help_text="格式: [{\"key\": \"A\", \"text\": \"选项内容\"}, ...]"
    )
    
    correct_answer = models.CharField(
        max_length=10, 
        verbose_name="正确答案",
        help_text="单选题格式: A，多选题格式: A,B,C"
    )
    
    explanation = RichTextField(
        blank=True, 
        verbose_name="答案解析",
        help_text="题目答案的详细解析"
    )
    
    # 分类和标签
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="所属分类"
    )
    
    tags = models.ManyToManyField(
        QuestionTag,
        blank=True,
        verbose_name="标签"
    )
    
    # 难度和分值
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name="难度等级"
    )
    
    score = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="题目分值"
    )
    
    # 编程语言
    LANGUAGE_CHOICES = [
        ('cpp', 'C++'),
        ('c', 'C'),
        ('java', 'Java'),
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('php', 'PHP'),
        ('csharp', 'C#'),
        ('ruby', 'Ruby'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('typescript', 'TypeScript'),
        ('scala', 'Scala'),
        ('perl', 'Perl'),
        ('r', 'R'),
        ('matlab', 'MATLAB'),
    ]
    
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True,
        verbose_name="编程语言",
        help_text="题目涉及的编程语言，用于代码高亮"
    )
    
    # 统计信息
    total_submit = models.IntegerField(
        default=0, 
        verbose_name="总提交次数"
    )
    
    total_accepted = models.IntegerField(
        default=0, 
        verbose_name="正确提交次数"
    )
    
    # 创建信息
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, 
        related_name="created_choice_questions",
        verbose_name="创建者"
    )
    
    # 状态
    visible = models.BooleanField(
        default=True, 
        verbose_name="是否可见"
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name="是否公开",
        help_text="是否对所有用户公开"
    )
    
    class Meta:
        db_table = "choice_question"
        verbose_name = "选择题"
        verbose_name_plural = "选择题"
        ordering = ['-create_time']
        
    def __str__(self):
        return f"[{self._id}] {self.title[:50]}"
    
    @property
    def acceptance_rate(self):
        """
        计算正确率
        """
        if self.total_submit == 0:
            return 0
        return round((self.total_accepted / self.total_submit) * 100, 2)
    
    def get_options_list(self):
        """
        获取选项列表
        """
        if isinstance(self.options, list):
            return self.options
        return []
    
    def get_correct_answer_list(self):
        """
        获取正确答案列表
        """
        if ',' in self.correct_answer:
            return self.correct_answer.split(',')
        return [self.correct_answer]
    
    def check_answer(self, user_answer):
        """
        检查用户答案是否正确
        """
        if self.question_type == 'single':
            return user_answer == self.correct_answer
        else:
            # 多选题需要完全匹配
            user_answers = set(user_answer.split(',')) if ',' in user_answer else {user_answer}
            correct_answers = set(self.get_correct_answer_list())
            return user_answers == correct_answers
    
    def update_statistics(self, is_correct):
        """
        更新统计信息
        """
        self.total_submit += 1
        if is_correct:
            self.total_accepted += 1
        self.save(update_fields=['total_submit', 'total_accepted'])
    
    @classmethod
    def get_random_questions(cls, count=10, category=None, difficulty=None):
        """
        随机获取题目
        """
        queryset = cls.objects.filter(visible=True, is_public=True)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset.order_by('?')[:count]