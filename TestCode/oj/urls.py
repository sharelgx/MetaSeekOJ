from django.contrib import admin
from django.urls import include, re_path as url
from django.shortcuts import redirect
from django.http import HttpResponse

def home_view(request):
    """根路径视图，重定向到管理界面"""
    return redirect('/admin/')

urlpatterns = [
    url(r"^$", home_view, name='home'),
    url(r"^admin/", admin.site.urls),
    url(r"^api/", include("account.urls.oj")),
    url(r"^api/admin/", include("account.urls.admin")),
    url(r"^api/", include("announcement.urls.oj")),
    url(r"^api/admin/", include("announcement.urls.admin")),
    url(r"^api/", include("conf.urls.oj")),
    url(r"^api/admin/", include("conf.urls.admin")),
    url(r"^api/", include("problem.urls.oj")),
    url(r"^api/admin/", include("problem.urls.admin")),
    url(r"^api/", include("contest.urls.oj")),
    url(r"^api/admin/", include("contest.urls.admin")),
    url(r"^api/", include("submission.urls.oj")),
    url(r"^api/admin/", include("submission.urls.admin")),
    url(r"^api/plugin/choice/", include("choice_question.urls")),
    url(r"^api/admin/", include("choice_question.admin_urls")),
    url(r"^api/judge/", include("judge.urls")),
    url(r"^api/admin/", include("utils.urls")),
]
