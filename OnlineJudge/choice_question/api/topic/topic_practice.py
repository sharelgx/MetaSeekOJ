# -*- coding: utf-8 -*-
"""
专题试做功能API
"""

from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Avg
from utils.api import APIView, validate_serializer
from account.decorators import login_required
from ...models import Category, ChoiceQuestion, ExamPaper, ExamSession
from ...serializers import ChoiceQuestionCategorySerializer
from django.db import transaction
import json


class TopicPracticeAPI(APIView):
    """
    专题练习主页API - 复用现有的分类系统
    """
    
    def get(self, request):
        """
        获取专题练习主页数据
        """
        # 获取所有根分类（一级分类）
        root_categories = Category.objects.filter(
            parent=None,
            is_active=True
        ).order_by('order', 'name')
        
        # 为每个分类添加统计信息
        categories_data = []
        for category in root_categories:
            # 获取该分类及其子分类下的所有题目数量
            all_questions_count = category.get_all_questions().count()
            
            category_data = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'question_count': all_questions_count,
                'level': 1,
                'has_children': category.get_children().exists(),
                'icon': 'el-icon-collection'  # 默认图标
            }
            categories_data.append(category_data)
        
        # 如果用户已登录，获取最近的练习记录
        recent_records = []
        if request.user.is_authenticated:
            recent_sessions = ExamSession.objects.filter(
                user=request.user,
                paper__title__startswith='专题练习：'  # 专题练习的试卷标题格式
            ).order_by('-create_time')[:5]
            
            for session in recent_sessions:
                record = {
                    'id': session.id,
                    'title': session.paper.title,
                    'status': session.status,
                    'score': session.score,
                    'correct_count': session.correct_count,
                    'total_count': session.total_count,
                    'create_time': session.create_time.strftime('%Y-%m-%d %H:%M'),
                    'can_continue': session.status == 'started'
                }
                recent_records.append(record)
        
        return self.success({
            'categories': categories_data,
            'recent_records': recent_records
        })


class TopicPracticeDetailAPI(APIView):
    """
    专题分类详情API
    """
    
    def get(self, request, category_id):
        """
        获取分类详情和题目列表
        """
        try:
            category = Category.objects.get(id=category_id, is_active=True)
        except Category.DoesNotExist:
            return self.error("专题分类不存在", status_code=404)
        
        # 获取子分类
        child_categories = []
        children = category.get_children().filter(is_active=True).order_by('order', 'name')
        for child in children:
            child_data = {
                'id': child.id,
                'name': child.name,
                'description': child.description,
                'question_count': child.get_all_questions().count(),
                'level': child.level
            }
            child_categories.append(child_data)
        
        # 获取当前分类的题目列表
        questions = category.get_all_questions().order_by('id')  # 按导入顺序排序
        questions_data = []
        for idx, question in enumerate(questions, 1):
            question_data = {
                'id': question.id,
                'title': question.title,
                'difficulty': question.difficulty,
                'question_type': question.question_type,
                'order': idx
            }
            questions_data.append(question_data)
        
        # 构建面包屑导航
        breadcrumb = []
        for ancestor in category.get_ancestors(include_self=True):
            breadcrumb.append({
                'id': ancestor.id,
                'name': ancestor.name
            })
        
        return self.success({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'level': category.level,
                'question_count': len(questions_data)
            },
            'child_categories': child_categories,
            'questions': questions_data,
            'breadcrumb': breadcrumb
        })


class TopicPracticeStartAPI(APIView):
    """
    开始专题练习API
    """
    
    @login_required
    def post(self, request):
        """
        开始专题练习
        """
        category_id = request.data.get('category_id')
        if not category_id:
            return self.error("缺少分类ID")
        
        try:
            category = Category.objects.get(id=category_id, is_active=True)
        except Category.DoesNotExist:
            return self.error("专题分类不存在")
        
        # 获取分类下的所有题目
        questions = list(category.get_all_questions().order_by('id'))  # 按导入顺序
        if not questions:
            return self.error("该专题下没有题目")
        
        # 创建或获取专题练习试卷
        paper_title = f"专题练习：{category.get_full_name()}"
        
        with transaction.atomic():
            # 检查是否已有进行中的练习
            existing_session = ExamSession.objects.filter(
                user=request.user,
                paper__title=paper_title,
                status='started'
            ).first()
            
            if existing_session:
                return self.success({
                    'session_id': existing_session.id,
                    'continue': True,
                    'redirect_url': f'/exam/session/{existing_session.id}/'
                })
            
            # 创建专题练习试卷（如果不存在）
            paper, created = ExamPaper.objects.get_or_create(
                title=paper_title,
                defaults={
                    'description': f'专题练习：{category.description}',
                    'duration': 60,  # 默认60分钟
                    'total_score': len(questions) * 2,  # 每题2分
                    'question_count': len(questions),
                    'paper_type': 'fixed',  # 固定题目
                    'created_by': request.user
                }
            )
            
            # 如果是新创建的试卷，关联题目
            if created:
                from ...models import ExamPaperQuestion
                for idx, question in enumerate(questions, 1):
                    ExamPaperQuestion.objects.create(
                        paper=paper,
                        question=question,
                        order=idx,
                        score=2
                    )
            
            # 创建考试会话
            session = ExamSession.objects.create(
                paper=paper,
                user=request.user,
                questions=[q.id for q in questions],
                total_count=len(questions)
            )
            
            # 开始考试
            session.start_exam()
            
        return self.success({
            'session_id': session.id,
            'continue': False,
            'redirect_url': f'/exam/session/{session.id}/'
        })


class TopicPracticeSubmitAPI(APIView):
    """
    专题练习提交API
    """
    
    @login_required
    def post(self, request, session_id):
        """
        提交专题练习
        """
        try:
            session = ExamSession.objects.get(
                id=session_id,
                user=request.user,
                status='started'
            )
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在或已结束")
        
        # 更新答案
        answers = request.data.get('answers', {})
        session.answers.update(answers)
        
        # 提交考试
        session.submit_exam()
        
        return self.success({
            'score': session.score,
            'correct_count': session.correct_count,
            'total_count': session.total_count,
            'status': session.status,
            'redirect_url': f'/exam/result/{session.id}/'
        })


class TopicPracticeListAPI(APIView):
    """
    专题练习记录列表API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户的专题练习记录列表
        """
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 获取专题练习记录
        sessions = ExamSession.objects.filter(
            user=request.user,
            paper__title__startswith='专题练习：'
        ).order_by('-create_time')
        
        # 分页
        total = sessions.count()
        start = (page - 1) * page_size
        end = start + page_size
        sessions = sessions[start:end]
        
        records = []
        for session in sessions:
            record = {
                'id': session.id,
                'title': session.paper.title.replace('专题练习：', ''),
                'status': session.status,
                'score': session.score,
                'correct_count': session.correct_count,
                'total_count': session.total_count,
                'start_time': session.start_time.strftime('%Y-%m-%d %H:%M') if session.start_time else None,
                'submit_time': session.submit_time.strftime('%Y-%m-%d %H:%M') if session.submit_time else None,
                'duration': None
            }
            
            # 计算用时
            if session.start_time and session.submit_time:
                duration = session.submit_time - session.start_time
                record['duration'] = f"{duration.seconds // 60}分{duration.seconds % 60}秒"
            
            records.append(record)
        
        return self.success({
            'records': records,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_next': end < total
        })