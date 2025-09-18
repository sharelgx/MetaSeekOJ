# -*- coding: utf-8 -*-
"""
Choice Question Plugin API Views
"""

# Question APIs
from .question import (
    ChoiceQuestionAPI,
    ChoiceQuestionDetailAPI,
    ChoiceQuestionSubmitAPI,
    ChoiceQuestionRandomAPI,
    ChoiceQuestionStatisticsAPI
)

# Category APIs
from .category import (
    CategoryAPI,
    CategoryDetailAPI,
    CategoryMoveAPI,
    CategoryStatisticsAPI
)

# Wrong Question APIs
from .wrong_question import (
    WrongQuestionAPI,
    WrongQuestionDetailAPI,
    WrongQuestionBatchAPI,
    WrongQuestionStatisticsAPI,
    WrongQuestionReviewAPI
)

# Tag APIs
from .tag import (
    QuestionTagAPI,
    QuestionTagDetailAPI,
    QuestionTagBatchAPI,
    QuestionTagStatisticsAPI
)

# Statistics APIs
from .statistics import (
    OverallStatisticsAPI,
    UserStatisticsAPI,
    QuestionStatisticsDetailAPI,
    CategoryStatisticsAPI,
    DifficultyStatisticsAPI,
    SubmissionTrendAPI,
    PopularQuestionsAPI,
    WrongQuestionAnalysisAPI,
    SystemHealthAPI
)

# Import/Export APIs
from .import_export import (
    QuestionImportAPI,
    QuestionExportAPI,
    QuestionTemplateAPI,
    ImportHistoryAPI,
    BatchOperationAPI
)

__all__ = [
    # Question APIs
    'ChoiceQuestionAPI',
    'ChoiceQuestionDetailAPI',
    'ChoiceQuestionSubmitAPI',
    'ChoiceQuestionRandomAPI',
    'ChoiceQuestionStatisticsAPI',
    
    # Category APIs
    'CategoryAPI',
    'CategoryDetailAPI',
    'CategoryMoveAPI',
    'CategoryStatisticsAPI',
    
    # Wrong Question APIs
    'WrongQuestionAPI',
    'WrongQuestionDetailAPI',
    'WrongQuestionBatchAPI',
    'WrongQuestionStatisticsAPI',
    'WrongQuestionReviewAPI',
    
    # Tag APIs
    'QuestionTagAPI',
    'QuestionTagDetailAPI',
    'QuestionTagBatchAPI',
    'QuestionTagStatisticsAPI',
    
    # Statistics APIs
    'OverallStatisticsAPI',
    'UserStatisticsAPI',
    'QuestionStatisticsDetailAPI',
    'CategoryStatisticsAPI',
    'DifficultyStatisticsAPI',
    'SubmissionTrendAPI',
    'PopularQuestionsAPI',
    'WrongQuestionAnalysisAPI',
    'SystemHealthAPI',
]
"""
选择题插件API模块
"""