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
from .admin_views_topic import (
    TopicPracticeRecordsAdminAPI,
    TopicPracticeStatisticsAdminAPI,
    TopicPracticeExportAdminAPI
)
from .views import ChoiceQuestionImportAPI
from .api.exam import ExamPaperImportAPI

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
    
    # 试卷导入
    re_path(r"^exam_paper/import/?$", ExamPaperImportAPI.as_view(), name="exam_paper_import"),
    
    # 专题试做管理
    re_path(r"^topic_practice/records/?$", TopicPracticeRecordsAdminAPI.as_view(), name="topic_practice_records_admin"),
    re_path(r"^topic_practice/records/(?P<record_id>\d+)/?$", TopicPracticeRecordsAdminAPI.as_view(), name="topic_practice_record_detail_admin"),
    re_path(r"^topic_practice/statistics/?$", TopicPracticeStatisticsAdminAPI.as_view(), name="topic_practice_statistics_admin"),
    re_path(r"^topic_practice/export/?$", TopicPracticeExportAdminAPI.as_view(), name="topic_practice_export_admin"),
]