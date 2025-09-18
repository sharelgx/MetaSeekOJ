# -*- coding: utf-8 -*-
"""
插件基础模型类
所有插件模型都应该继承此基类
"""

from django.db import models
from django.utils import timezone


class PluginBaseModel(models.Model):
    """
    插件基础模型类
    提供统一的表名前缀和基础字段
    """
    
    # 基础时间字段
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    
    # 插件标识
    plugin_version = models.CharField(max_length=20, default="1.0.0", verbose_name="插件版本")
    
    class Meta:
        abstract = True
        
    @classmethod
    def get_table_name(cls, model_name):
        """
        获取带插件前缀的表名
        """
        return f"choice_plugin_{model_name}"
    
    def save(self, *args, **kwargs):
        """
        重写save方法，添加插件特定逻辑
        """
        # 更新时间戳
        if not self.pk:
            self.create_time = timezone.now()
        self.last_update_time = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        """
        默认字符串表示
        """
        if hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'title'):
            return self.title
        else:
            return f"{self.__class__.__name__}({self.pk})"