from django.urls import re_path
from .views import (
    ChoiceQuestionCategoryAPI,
    ChoiceQuestionTagAPI,
    ChoiceQuestionAPI,
    ChoiceQuestionDetailAPI,
    ChoiceQuestionSubmissionAPI,
    WrongQuestionAPI,
    ChoiceQuestionStatsAPI
)
from .api.exam import (
    exam_paper_list,
    exam_paper_detail,
    exam_paper_generate_preview,
    exam_session_create,
    exam_session_start,
    exam_session_detail,
    exam_session_answer,
    exam_session_submit,
    exam_session_list
)

app_name = 'choice_question'

urlpatterns = [
    # 分类管理 - RESTful API
    re_path(r"^categories/?$", ChoiceQuestionCategoryAPI.as_view(), name="category-list"),
    re_path(r"^categories/(?P<pk>\d+)/?$", ChoiceQuestionCategoryAPI.as_view(), name="category-detail"),
    
    # 标签管理 - RESTful API
    re_path(r"^tags/?$", ChoiceQuestionTagAPI.as_view(), name="tag-list"),
    re_path(r"^tags/(?P<pk>\d+)/?$", ChoiceQuestionTagAPI.as_view(), name="tag-detail"),
    
    # 选择题管理 - RESTful API
    re_path(r"^questions/?$", ChoiceQuestionAPI.as_view(), name="question-list"),
    re_path(r"^questions/(?P<pk>\d+)/?$", ChoiceQuestionDetailAPI.as_view(), name="question-detail"),
    
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
    
    # 试卷管理
    re_path(r"^exam-papers/?$", exam_paper_list, name="exam-paper-list"),
    re_path(r"^exam-papers/(?P<paper_id>\d+)/?$", exam_paper_detail, name="exam-paper-detail"),
    re_path(r"^exam-papers/generate-preview/?$", exam_paper_generate_preview, name="exam-paper-generate-preview"),
    
    # 考试会话管理
    re_path(r"^exam-sessions/?$", exam_session_list, name="exam-session-list"),
    re_path(r"^exam-sessions/create/?$", exam_session_create, name="exam-session-create"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/?$", exam_session_detail, name="exam-session-detail"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/start/?$", exam_session_start, name="exam-session-start"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/answer/?$", exam_session_answer, name="exam-session-answer"),
    re_path(r"^exam-sessions/(?P<session_id>\d+)/submit/?$", exam_session_submit, name="exam-session-submit"),
]