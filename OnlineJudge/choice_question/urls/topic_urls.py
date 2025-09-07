# -*- coding: utf-8 -*-
"""
专题功能URL配置
"""

from django.urls import path
from ..api.topic_views import (
    TopicAPI, TopicDetailAPI, TopicPracticeAPI, TopicPracticeRecordAPI,
    TopicWrongQuestionAPI, TopicWrongQuestionStatisticsAPI, TopicStatisticsAPI
)

urlpatterns = [
    # 专题管理
    path('topics/', TopicAPI.as_view(), name='topic_list_create'),
    path('topics/<int:topic_id>/', TopicDetailAPI.as_view(), name='topic_detail'),
    
    # 专题练习
    path('topics/<int:topic_id>/practice/', TopicPracticeAPI.as_view(), name='topic_practice'),
    path('topics/practice/submit/', TopicPracticeAPI.as_view(), name='topic_practice_submit'),
    
    # 练习记录
    path('topics/practice/records/', TopicPracticeRecordAPI.as_view(), name='topic_practice_records'),
    
    # 专题错题
    path('topics/wrong-questions/', TopicWrongQuestionAPI.as_view(), name='topic_wrong_questions'),
    path('topics/wrong-questions/<int:record_id>/', TopicWrongQuestionAPI.as_view(), name='topic_wrong_question_detail'),
    path('topics/wrong-questions/statistics/', TopicWrongQuestionStatisticsAPI.as_view(), name='topic_wrong_question_statistics'),
    
    # 专题统计
    path('topics/<int:topic_id>/statistics/', TopicStatisticsAPI.as_view(), name='topic_statistics'),
]