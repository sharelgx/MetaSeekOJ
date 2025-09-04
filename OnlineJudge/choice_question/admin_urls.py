# -*- coding: utf-8 -*-
"""
选择题管理员URL配置
"""

from django.urls import re_path
from .admin_views import (
    ChoiceQuestionAdminAPI,
    ChoiceQuestionCategoryAdminAPI,
    ChoiceQuestionTagAdminAPI
)
from .views import ChoiceQuestionImportAPI

app_name = 'choice_question_admin'

urlpatterns = [
    # 选择题管理
    re_path(r"^choice_question/?$", ChoiceQuestionAdminAPI.as_view(), name="choice_question_admin"),
    
    # 选择题批量操作
    re_path(r"^choice_question/batch_operation/?$", ChoiceQuestionAdminAPI.as_view(), name="choice_question_batch_operation"),
    
    # 选择题导入
    re_path(r"^choice_question/import/?$", ChoiceQuestionImportAPI.as_view(), name="choice_question_import"),
    
    # 分类管理
    re_path(r"^choice_question/categories/?$", ChoiceQuestionCategoryAdminAPI.as_view(), name="choice_question_categories_admin"),
    
    # 标签管理
    re_path(r"^choice_question/tags/?$", ChoiceQuestionTagAdminAPI.as_view(), name="choice_question_tags_admin"),
]