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

app_name = 'choice_question_admin'

urlpatterns = [
    # 选择题管理
    re_path(r"^choice_question/?$", ChoiceQuestionAdminAPI.as_view(), name="choice_question_admin"),
    
    # 分类管理
    re_path(r"^choice_question/categories/?$", ChoiceQuestionCategoryAdminAPI.as_view(), name="choice_question_categories_admin"),
    
    # 标签管理
    re_path(r"^choice_question/tags/?$", ChoiceQuestionTagAdminAPI.as_view(), name="choice_question_tags_admin"),
]