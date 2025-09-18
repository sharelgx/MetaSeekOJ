# -*- coding: utf-8 -*-
"""
选择题插件模型模块
"""

from .base import PluginBaseModel
from .category import Category
from .tag import QuestionTag
from .question import ChoiceQuestion
from .submission import ChoiceQuestionSubmission
from .wrong_question import WrongQuestion
from .exam import ExamPaper, ExamSession, ExamPaperQuestion
from .topic import (
    Topic, 
    TopicCategoryRelation, 
    TopicTagRelation, 
    TopicQuestion,
    TopicPracticeRecord,
    TopicWrongQuestionRecord
)

__all__ = [
    'PluginBaseModel',
    'Category',
    'QuestionTag',
    'ChoiceQuestion',
    'ChoiceQuestionSubmission',
    'WrongQuestion',
    'ExamPaper',
    'ExamSession',
    'ExamPaperQuestion',
    'Topic',
    'TopicCategoryRelation',
    'TopicTagRelation',
    'TopicQuestion',
    'TopicPracticeRecord',
    'TopicWrongQuestionRecord',
]