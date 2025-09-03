# -*- coding: utf-8 -*-
"""
序列化器模块
"""

from .base import (
    UserSerializer,
    ChoiceQuestionCategorySerializer,
    ChoiceQuestionTagSerializer,
    ChoiceQuestionListSerializer,
    ChoiceQuestionDetailSerializer,
    ChoiceQuestionCreateSerializer,
    ChoiceQuestionSubmissionSerializer,
    ChoiceQuestionSubmissionCreateSerializer,
    WrongQuestionSerializer
)

from .exam import (
    ExamPaperListSerializer,
    ExamPaperDetailSerializer,
    ExamPaperCreateSerializer,
    ExamPaperQuestionSerializer,
    ExamSessionListSerializer,
    ExamSessionDetailSerializer,
    ExamSessionCreateSerializer,
    ExamAnswerSerializer,
    ExamSubmitSerializer
)

__all__ = [
    # 基础序列化器
    'UserSerializer',
    'ChoiceQuestionCategorySerializer',
    'ChoiceQuestionTagSerializer',
    'ChoiceQuestionListSerializer',
    'ChoiceQuestionDetailSerializer',
    'ChoiceQuestionCreateSerializer',
    'ChoiceQuestionSubmissionSerializer',
    'ChoiceQuestionSubmissionCreateSerializer',
    'WrongQuestionSerializer',
    
    # 试卷序列化器
    'ExamPaperListSerializer',
    'ExamPaperDetailSerializer',
    'ExamPaperCreateSerializer',
    'ExamPaperQuestionSerializer',
    'ExamSessionListSerializer',
    'ExamSessionDetailSerializer',
    'ExamSessionCreateSerializer',
    'ExamAnswerSerializer',
    'ExamSubmitSerializer',
]