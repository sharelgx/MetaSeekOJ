# 测试URL配置
from django.urls import path, include

urlpatterns = [
    path('api/choice_question/', include('choice_question.urls')),
]