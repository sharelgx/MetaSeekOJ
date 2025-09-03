from django.urls import re_path
from .views import (
    ChoiceQuestionCategoryAPI,
    ChoiceQuestionTagAPI,
    ChoiceQuestionAPI,
    ChoiceQuestionDetailAPI,
    ChoiceQuestionSubmissionAPI,
    ChoiceQuestionStatsAPI,
    ChoiceQuestionImportAPI
)
from .api.category import CategoryAPI, CategoryDetailAPI, CategoryMoveAPI, CategoryStatisticsAPI
from .api.tag import QuestionTagAPI, QuestionTagDetailAPI, QuestionTagBatchAPI, QuestionTagStatisticsAPI
from .api.question import ChoiceQuestionSubmitAPI
from .api.wrong_question import WrongQuestionAPI
from .api.exam import (
    ExamPaperAPI,
    ExamSessionAPI,
    ExamSessionActionAPI
)

app_name = 'choice_question'

urlpatterns = [
    # 分类管理 - RESTful API
    re_path(r"^categories/?$", CategoryAPI.as_view(), name="category-list"),
    re_path(r"^categories/(?P<category_id>\d+)/?$", CategoryDetailAPI.as_view(), name="category-detail"),
    re_path(r"^categories/(?P<category_id>\d+)/move/?$", CategoryMoveAPI.as_view(), name="category-move"),
    re_path(r"^categories/(?P<category_id>\d+)/statistics/?$", CategoryStatisticsAPI.as_view(), name="category-statistics"),
    re_path(r"^categories/batch-update/?$", CategoryAPI.as_view(), name="category-batch-update"),
    re_path(r"^categories/batch-delete/?$", CategoryAPI.as_view(), name="category-batch-delete"),
    
    # 标签管理 - RESTful API
    re_path(r"^tags/?$", QuestionTagAPI.as_view(), name="tag-list"),
    re_path(r"^tags/(?P<tag_id>\d+)/?$", QuestionTagDetailAPI.as_view(), name="tag-detail"),
    re_path(r"^tags/batch-delete/?$", QuestionTagBatchAPI.as_view(), name="tag-batch-delete"),
    re_path(r"^tags/statistics/?$", QuestionTagStatisticsAPI.as_view(), name="tag-statistics"),
    
    # 选择题管理 - RESTful API
    re_path(r"^questions/?$", ChoiceQuestionAPI.as_view(), name="question-list"),
    re_path(r"^questions/(?P<pk>\d+)/?$", ChoiceQuestionDetailAPI.as_view(), name="question-detail"),
    re_path(r"^questions/(?P<question_id>\d+)/submit/?$", ChoiceQuestionSubmitAPI.as_view(), name="question-submit"),
    re_path(r"^questions/import/?$", ChoiceQuestionImportAPI.as_view(), name="question-import"),
    
    # 提交记录 - RESTful API
    re_path(r"^submissions/?$", ChoiceQuestionSubmissionAPI.as_view(), name="submission-list"),
    re_path(r"^submissions/(?P<pk>\d+)/?$", ChoiceQuestionSubmissionAPI.as_view(), name="submission-detail"),
    
    # 错题本管理 - RESTful API
    re_path(r"^wrong-questions/?$", WrongQuestionAPI.as_view(), name="wrong-question-list"),
    re_path(r"^wrong-questions/(?P<pk>\d+)/?$", WrongQuestionAPI.as_view(), name="wrong-question-detail"),
    re_path(r"^wrong-questions/(?P<pk>\d+)/resolve/?$", WrongQuestionAPI.as_view(), name="wrong-question-resolve"),
     
    # 统计分析
    re_path(r"^statistics/?$", ChoiceQuestionStatsAPI.as_view(), name="statistics"),
    re_path(r"^statistics/user/?$", ChoiceQuestionStatsAPI.as_view(), name="user-statistics"),
    re_path(r"^statistics/admin/?$", ChoiceQuestionStatsAPI.as_view(), name="admin-statistics"),
    
    # 试卷管理 - RESTful API
    re_path(r"^exam-papers/?$", ExamPaperAPI.as_view(), name="exam-paper-list"),
    re_path(r"^exam-papers/(?P<paper_id>\d+)/?$", ExamPaperAPI.as_view(), name="exam-paper-detail"),
    re_path(r"^exam-papers/generate-preview/?$", ExamPaperAPI.as_view(), name="exam-paper-generate-preview"),
    
    # 考试会话管理 - RESTful API
    re_path(r"^exam-sessions/?$", ExamSessionAPI.as_view(), name="exam-session-list"),
    re_path(r"^exam-sessions/create/?$", ExamSessionAPI.as_view(), name="exam-session-create"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/?$", ExamSessionAPI.as_view(), name="exam-session-detail"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/start/?$", ExamSessionActionAPI.as_view(), name="exam-session-start"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/answer/?$", ExamSessionActionAPI.as_view(), name="exam-session-answer"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/submit/?$", ExamSessionActionAPI.as_view(), name="exam-session-submit"),
]