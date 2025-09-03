# -*- coding: utf-8 -*-
"""
统一判题系统URL配置
"""

from django.urls import path
from .unified_api import (
    UnifiedSubmissionAPI,
    UnifiedSubmissionListAPI,
    UserStatisticsAPI,
    SubmissionDetailAPI,
    JudgeStatusAPI
)
from .mixed_question_api import (
    MixedQuestionListAPI,
    MixedQuestionStatisticsAPI
)

app_name = 'judge'

urlpatterns = [
    # 统一提交接口
    path('submit/', UnifiedSubmissionAPI.as_view(), name='unified_submit'),
    
    # 提交记录列表
    path('submissions/', UnifiedSubmissionListAPI.as_view(), name='submission_list'),
    
    # 提交详情
    path('submission/detail/', SubmissionDetailAPI.as_view(), name='submission_detail'),
    
    # 判题状态查询
    path('status/', JudgeStatusAPI.as_view(), name='judge_status'),
    
    # 用户统计信息
    path('statistics/', UserStatisticsAPI.as_view(), name='user_statistics'),
    
    # 混合题目查询
    path('questions/', MixedQuestionListAPI.as_view(), name='mixed_question_list'),
    
    # 混合题目统计
    path('questions/statistics/', MixedQuestionStatisticsAPI.as_view(), name='mixed_question_statistics'),
]