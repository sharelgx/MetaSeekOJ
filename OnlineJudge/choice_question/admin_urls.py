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
    re_path(r"^choice_question/category/?$", ChoiceQuestionCategoryAdminAPI.as_view(), name="choice_question_category_admin"),
    
    # 标签管理
    re_path(r"^choice_question/tag/?$", ChoiceQuestionTagAdminAPI.as_view(), name="choice_question_tag_admin"),
]