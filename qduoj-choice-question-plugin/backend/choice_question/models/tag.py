# -*- coding: utf-8 -*-
"""
选择题标签模型
"""

from django.db import models
from django.core.validators import RegexValidator
from .base import PluginBaseModel


class QuestionTag(PluginBaseModel):
    """
    选择题标签模型
    """
    
    name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="标签名称",
        help_text="标签名称，不能重复"
    )
    
    color = models.CharField(
        max_length=7, 
        default='#409EFF',
        verbose_name="标签颜色",
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='颜色格式必须为 #RRGGBB'
            )
        ],
        help_text="标签显示颜色，格式为 #RRGGBB"
    )
    
    description = models.TextField(
        blank=True, 
        verbose_name="标签描述",
        help_text="标签的详细描述"
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        help_text="是否启用此标签"
    )
    
    # 统计信息
    question_count = models.IntegerField(
        default=0, 
        verbose_name="关联题目数量",
        help_text="使用此标签的题目数量"
    )
    
    # 标签类型
    TAG_TYPE_CHOICES = [
        ('difficulty', '难度标签'),
        ('subject', '学科标签'),
        ('knowledge', '知识点标签'),
        ('custom', '自定义标签'),
    ]
    
    tag_type = models.CharField(
        max_length=20,
        choices=TAG_TYPE_CHOICES,
        default='custom',
        verbose_name="标签类型"
    )
    
    class Meta:
        db_table = "choice_plugin_tag"
        verbose_name = "选择题标签"
        verbose_name_plural = "选择题标签"
        ordering = ['tag_type', 'name']
        
    def __str__(self):
        return self.name
    
    def update_question_count(self):
        """
        更新关联题目数量
        """
        from .question import ChoiceQuestion
        self.question_count = ChoiceQuestion.objects.filter(
            tags=self,
            visible=True
        ).count()
        self.save(update_fields=['question_count'])
    
    @classmethod
    def get_popular_tags(cls, limit=10):
        """
        获取热门标签（按题目数量排序）
        """
        return cls.objects.filter(
            is_active=True,
            question_count__gt=0
        ).order_by('-question_count')[:limit]
    
    @classmethod
    def get_tags_by_type(cls, tag_type):
        """
        根据类型获取标签
        """
        return cls.objects.filter(
            tag_type=tag_type,
            is_active=True
        ).order_by('name')