# -*- coding: utf-8 -*-
"""
选择题API视图
"""

from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
# from utils.shortcuts import paginate_data  # 使用APIView的paginate_data方法
from account.decorators import login_required, super_admin_required
from ..models import ChoiceQuestion, Category, QuestionTag, ChoiceQuestionSubmission, WrongQuestion
from ..serializers import (
    ChoiceQuestionListSerializer,
    ChoiceQuestionDetailSerializer,
    ChoiceQuestionCreateSerializer,
    ChoiceQuestionSubmissionSerializer,
    ChoiceQuestionSubmissionCreateSerializer
)
from ..utils.judge import ChoiceQuestionJudge
from ..utils.statistics import StatisticsCalculator


class ChoiceQuestionAPI(APIView):
    """
    选择题API
    """
    
    def get(self, request):
        """
        获取选择题列表
        """
        print("=== ChoiceQuestionAPI GET方法被调用 ===")
        import logging
        logger = logging.getLogger('choice_question.api.question')
        
        # 获取查询参数
        category_id = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        tag_ids = request.GET.get('tags', '').split(',') if request.GET.get('tags') else []
        keyword = request.GET.get('keyword', '').strip()
        is_public = request.GET.get('is_public')
        question_type = request.GET.get('question_type')
        
        # 添加调试日志
        print(f"[DEBUG] ChoiceQuestionAPI GET请求参数: category={category_id}, difficulty={difficulty}, tags={tag_ids}, keyword={keyword}, is_public={is_public}, question_type={question_type}")
        logger.info(f"ChoiceQuestionAPI GET请求参数: category={category_id}, difficulty={difficulty}, tags={tag_ids}, keyword={keyword}, is_public={is_public}, question_type={question_type}")
        
        # 构建查询条件
        print(f"[DEBUG] API被调用，category参数: {request.GET.get('category')}")
        queryset = ChoiceQuestion.objects.filter(visible=True)
        print(f"[DEBUG] 初始查询集数量: {queryset.count()}")
        logger.info(f"初始查询集数量: {queryset.count()}")
        
        # 分类筛选
        if category_id:
            print(f"[DEBUG] 开始分类筛选，category_id: {category_id}")
            try:
                category = Category.objects.get(id=category_id)
                # 包含子分类的题目
                categories = category.get_descendants(include_self=True)
                print(f"[DEBUG] 找到分类: {category.name}，子分类数量: {len(categories)}")
                queryset = queryset.filter(category__in=categories)
                print(f"[DEBUG] 分类筛选后查询集数量: {queryset.count()}")
                logger.info(f"分类筛选后查询集数量: {queryset.count()}")
            except Category.DoesNotExist:
                print(f"[DEBUG] 分类不存在: {category_id}")
                logger.warning(f"分类不存在: category_id={category_id}")
                pass
        
        # 难度筛选
        if difficulty and difficulty in ['easy', 'medium', 'hard']:
            queryset = queryset.filter(difficulty=difficulty)
            logger.info(f"难度筛选后查询集数量: {queryset.count()}")
        
        # 标签筛选
        if tag_ids and tag_ids != ['']:
            try:
                tag_ids = [int(tag_id) for tag_id in tag_ids if tag_id.isdigit()]
                if tag_ids:
                    queryset = queryset.filter(tags__id__in=tag_ids).distinct()
                    logger.info(f"标签筛选后查询集数量: {queryset.count()}")
            except ValueError:
                logger.warning(f"标签ID格式错误: {tag_ids}")
                pass
        
        # 题型筛选
        if question_type and question_type in ['single', 'multiple']:
            queryset = queryset.filter(question_type=question_type)
            logger.info(f"题型筛选后查询集数量: {queryset.count()}")
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(_id__icontains=keyword)
            )
            logger.info(f"关键词搜索后查询集数量: {queryset.count()}")
        
        # 公开性筛选
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
            logger.info(f"公开性筛选后查询集数量: {queryset.count()}")
        
        # 权限控制
        if not request.user.is_authenticated or not request.user.is_admin():
            queryset = queryset.filter(is_public=True)
            print(f"[DEBUG] 权限控制后查询集数量: {queryset.count()}")
            logger.info(f"权限控制后查询集数量: {queryset.count()}")
        else:
            print(f"[DEBUG] 管理员权限，跳过公开性筛选，查询集数量: {queryset.count()}")
            logger.info(f"管理员权限，跳过公开性筛选，查询集数量: {queryset.count()}")
        
        # 排序
        queryset = queryset.select_related('category', 'created_by').prefetch_related('tags')
        print(f"[DEBUG] 最终查询集数量: {queryset.count()}")
        logger.info(f"最终查询集数量: {queryset.count()}")
        
        return self.success(self.paginate_data(request, queryset, ChoiceQuestionListSerializer))
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionCreateSerializer)
    def post(self, request):
        """
        创建选择题
        """
        data = request.data
        data['created_by'] = request.user.id
        
        # 生成显示ID
        if not data.get('_id'):
            data['_id'] = self._generate_question_id()
        
        serializer = ChoiceQuestionCreateSerializer(data=data)
        if serializer.is_valid():
            question = serializer.save()
            return self.success(ChoiceQuestionDetailSerializer(question).data)
        return self.error(serializer.errors)
    
    def _generate_question_id(self):
        """
        生成题目显示ID
        """
        import uuid
        return str(uuid.uuid4())[:8].upper()


class ChoiceQuestionDetailAPI(APIView):
    """
    选择题详情API
    """
    
    def get(self, request, question_id):
        """
        获取选择题详情
        """
        try:
            question = ChoiceQuestion.objects.select_related(
                'category', 'created_by'
            ).prefetch_related('tags').get(id=question_id, visible=True)
            
            # 权限检查
            if not question.is_public and (
                not request.user.is_authenticated or not request.user.is_admin()
            ):
                return self.error("题目不存在或无权限访问", status_code=404)
            
            return self.success(ChoiceQuestionDetailSerializer(question).data)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionCreateSerializer)
    def put(self, request, question_id):
        """
        更新选择题
        """
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)
        
        serializer = ChoiceQuestionCreateSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            question = serializer.save()
            return self.success(ChoiceQuestionDetailSerializer(question).data)
        return self.error(serializer.errors)
    
    @super_admin_required
    def delete(self, request, question_id):
        """
        删除选择题
        """
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
            question.visible = False
            question.save()
            return self.success("删除成功")
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)


class ChoiceQuestionSubmitAPI(CSRFExemptAPIView):
    """
    选择题提交API
    """
    
    @login_required
    @validate_serializer(ChoiceQuestionSubmissionCreateSerializer)
    def post(self, request, question_id):
        """
        提交选择题答案
        """
        try:
            question = ChoiceQuestion.objects.get(id=question_id, visible=True)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)
        
        # 权限检查
        if not question.is_public and not request.user.is_admin():
            return self.error("题目不存在或无权限访问", status_code=404)
        
        user_answer = request.data.get('selected_answer', '').strip()
        time_spent = request.data.get('time_spent', 0)
        
        if not user_answer:
            return self.error("请选择答案")
        
        # 判题
        judge = ChoiceQuestionJudge()
        result = judge.judge_submission(question, user_answer, request.user)
        
        # 创建提交记录
        submission_data = {
            'question': question.id,
            'user': request.user.id,
            'selected_answer': user_answer,
            'is_correct': result['is_correct'],
            'score': result['score'],
            'time_spent': time_spent,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
        }
        
        submission_serializer = ChoiceQuestionSubmissionCreateSerializer(data=submission_data)
        if submission_serializer.is_valid():
            submission = submission_serializer.save()
            
            # 更新题目统计
            question.update_statistics(result['is_correct'])
            
            # 如果答错，添加到错题本
            if not result['is_correct']:
                WrongQuestion.add_or_update_wrong_question(
                    user=request.user,
                    question=question,
                    wrong_answer=user_answer
                )
            
            return self.success({
                'submission_id': submission.id,
                'is_correct': result['is_correct'],
                'score': result['score'],
                'correct_answer': question.correct_answer,
                'explanation': question.explanation
            })
        
        return self.error(submission_serializer.errors)
    
    def get_client_ip(self, request):
        """
        获取客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ChoiceQuestionRandomAPI(APIView):
    """
    随机选择题API
    """
    
    def get(self, request):
        """
        获取随机选择题
        """
        count = int(request.GET.get('count', 10))
        category_id = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        
        # 限制数量
        count = min(count, 50)
        
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        questions = ChoiceQuestion.get_random_questions(
            count=count,
            category=category,
            difficulty=difficulty
        )
        
        return self.success(QuestionListSerializer(questions, many=True).data)


class ChoiceQuestionStatisticsAPI(APIView):
    """
    选择题统计API
    """
    
    @super_admin_required
    def get(self, request, question_id):
        """
        获取题目统计信息
        """
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)
        
        statistics = QuestionStatistics.get_question_statistics(question)
        return self.success(statistics)