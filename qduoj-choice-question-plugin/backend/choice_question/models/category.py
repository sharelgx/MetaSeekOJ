# -*- coding: utf-8 -*-
"""
选择题分类模型
"""

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from .base import PluginBaseModel


class Category(MPTTModel, PluginBaseModel):
    """
    选择题分类模型（支持多级分类）
    使用django-mptt实现树形结构
    """
    
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name="父分类"
    )
    description = models.TextField(blank=True, verbose_name="分类描述")
    order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 统计信息
    question_count = models.IntegerField(default=0, verbose_name="题目数量")
    
    class MPTTMeta:
        order_insertion_by = ['order', 'name']
    
    class Meta:
        db_table = "choice_plugin_category"
        verbose_name = "选择题分类"
        verbose_name_plural = "选择题分类"
        ordering = ['tree_id', 'lft']
        
    def __str__(self):
        return self.name
    
    def get_full_name(self):
        """
        获取完整分类路径
        """
        names = [ancestor.name for ancestor in self.get_ancestors(include_self=True)]
        return ' > '.join(names)
    
    def update_question_count(self):
        """
        更新题目数量统计
        """
        from .question import ChoiceQuestion
        self.question_count = ChoiceQuestion.objects.filter(
            category=self,
            visible=True
        ).count()
        self.save(update_fields=['question_count'])
    
    def get_all_questions(self):
        """
        获取当前分类及其子分类下的所有题目
        """
        from .question import ChoiceQuestion
        descendant_categories = self.get_descendants(include_self=True)
        return ChoiceQuestion.objects.filter(
            category__in=descendant_categories,
            visible=True
        )