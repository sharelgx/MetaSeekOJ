# -*- coding: utf-8 -*-
"""
错题本API视图
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView, validate_serializer
from utils.api._serializers import PaginationSerializer
from utils.shortcuts import paginate_data
from account.decorators import login_required
from ..models import WrongQuestion, ChoiceQuestion, Category
from ..serializers import WrongQuestionSerializer, WrongQuestionDetailSerializer


class WrongQuestionAPI(APIView):
    """
    错题本API
    """
    
    @login_required
    @validate_serializer(PaginationSerializer)
    def get(self, request):
        """
        获取用户错题列表
        """
        # 获取查询参数
        is_mastered = request.GET.get('is_mastered')
        category_id = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        error_type = request.GET.get('error_type')
        keyword = request.GET.get('keyword', '').strip()
        
        # 构建查询条件
        queryset = WrongQuestion.objects.filter(user=request.user).select_related(
            'question', 'question__category'
        ).prefetch_related('question__tags')
        
        # 掌握状态筛选
        if is_mastered is not None:
            queryset = queryset.filter(is_mastered=is_mastered.lower() == 'true')
        
        # 分类筛选
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(question__category__in=categories)
            except Category.DoesNotExist:
                pass
        
        # 难度筛选
        if difficulty and difficulty in ['easy', 'medium', 'hard']:
            queryset = queryset.filter(question__difficulty=difficulty)
        
        # 错误类型筛选
        if error_type and error_type in ['careless', 'knowledge', 'comprehension', 'calculation', 'other']:
            queryset = queryset.filter(error_type=error_type)
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(question__title__icontains=keyword) |
                Q(question__description__icontains=keyword) |
                Q(note__icontains=keyword)
            )
        
        return self.success(paginate_data(request, queryset, WrongQuestionSerializer))
    
    @login_required
    def post(self, request):
        """
        手动添加错题
        """
        question_id = request.data.get('question_id')
        wrong_answer = request.data.get('wrong_answer', '')
        error_type = request.data.get('error_type', 'other')
        note = request.data.get('note', '')
        
        if not question_id:
            return self.error("请指定题目ID")
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id, visible=True)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在")
        
        # 权限检查
        if not question.is_public and not request.user.is_admin():
            return self.error("题目不存在或无权限访问")
        
        # 添加或更新错题记录
        wrong_question, created = WrongQuestion.add_or_update_wrong_question(
            user=request.user,
            question=question,
            wrong_answer=wrong_answer,
            error_type=error_type
        )
        
        # 更新笔记
        if note:
            wrong_question.note = note
            wrong_question.save()
        
        return self.success(WrongQuestionDetailSerializer(wrong_question).data)


class WrongQuestionDetailAPI(APIView):
    """
    错题详情API
    """
    
    @login_required
    def get(self, request, wrong_question_id):
        """
        获取错题详情
        """
        try:
            wrong_question = WrongQuestion.objects.select_related(
                'question', 'question__category', 'question__created_by'
            ).prefetch_related('question__tags').get(
                id=wrong_question_id, user=request.user
            )
            return self.success(WrongQuestionDetailSerializer(wrong_question).data)
        except WrongQuestion.DoesNotExist:
            return self.error("错题记录不存在", status_code=404)
    
    @login_required
    def put(self, request, wrong_question_id):
        """
        更新错题记录
        """
        try:
            wrong_question = WrongQuestion.objects.get(id=wrong_question_id, user=request.user)
        except WrongQuestion.DoesNotExist:
            return self.error("错题记录不存在", status_code=404)
        
        # 更新字段
        note = request.data.get('note')
        error_type = request.data.get('error_type')
        is_mastered = request.data.get('is_mastered')
        
        if note is not None:
            wrong_question.note = note
        
        if error_type and error_type in ['careless', 'knowledge', 'comprehension', 'calculation', 'other']:
            wrong_question.error_type = error_type
        
        if is_mastered is not None:
            if is_mastered:
                wrong_question.mark_as_mastered()
            else:
                wrong_question.is_mastered = False
                wrong_question.mastered_time = None
        
        wrong_question.save()
        return self.success(WrongQuestionDetailSerializer(wrong_question).data)
    
    @login_required
    def delete(self, request, wrong_question_id):
        """
        删除错题记录
        """
        try:
            wrong_question = WrongQuestion.objects.get(id=wrong_question_id, user=request.user)
            wrong_question.delete()
            return self.success("删除成功")
        except WrongQuestion.DoesNotExist:
            return self.error("错题记录不存在", status_code=404)


class WrongQuestionBatchAPI(APIView):
    """
    错题批量操作API
    """
    
    @login_required
    def post(self, request):
        """
        批量操作错题
        """
        action = request.data.get('action')  # mark_mastered, delete, update_error_type
        wrong_question_ids = request.data.get('wrong_question_ids', [])
        
        if not action or not wrong_question_ids:
            return self.error("请指定操作类型和错题ID列表")
        
        # 获取用户的错题记录
        wrong_questions = WrongQuestion.objects.filter(
            id__in=wrong_question_ids, user=request.user
        )
        
        if not wrong_questions.exists():
            return self.error("未找到有效的错题记录")
        
        success_count = 0
        
        if action == 'mark_mastered':
            # 批量标记为已掌握
            for wq in wrong_questions:
                wq.mark_as_mastered()
                success_count += 1
        
        elif action == 'delete':
            # 批量删除
            success_count = wrong_questions.count()
            wrong_questions.delete()
        
        elif action == 'update_error_type':
            # 批量更新错误类型
            error_type = request.data.get('error_type')
            if error_type not in ['careless', 'knowledge', 'comprehension', 'calculation', 'other']:
                return self.error("无效的错误类型")
            
            success_count = wrong_questions.update(error_type=error_type)
        
        else:
            return self.error("无效的操作类型")
        
        return self.success(f"成功处理 {success_count} 条记录")


class WrongQuestionStatisticsAPI(APIView):
    """
    错题统计API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户错题统计
        """
        statistics = WrongQuestion.get_user_statistics(request.user)
        return self.success(statistics)


class WrongQuestionReviewAPI(APIView):
    """
    错题复习API
    """
    
    @login_required
    def get(self, request):
        """
        获取复习题目列表
        """
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # 限制最大数量
        
        review_questions = WrongQuestion.get_review_questions(request.user, limit)
        return self.success(WrongQuestionSerializer(review_questions, many=True).data)
    
    @login_required
    def post(self, request):
        """
        提交复习结果
        """
        wrong_question_id = request.data.get('wrong_question_id')
        is_correct = request.data.get('is_correct', False)
        
        if not wrong_question_id:
            return self.error("请指定错题记录ID")
        
        try:
            wrong_question = WrongQuestion.objects.get(id=wrong_question_id, user=request.user)
        except WrongQuestion.DoesNotExist:
            return self.error("错题记录不存在")
        
        if is_correct:
            # 如果复习正确，标记为已掌握
            wrong_question.mark_as_mastered()
            message = "恭喜！已标记为掌握"
        else:
            # 如果复习错误，增加错误次数
            wrong_question.wrong_count += 1
            wrong_question.save()
            message = "继续加油！"
        
        return self.success({
            'message': message,
            'wrong_question': WrongQuestionDetailSerializer(wrong_question).data
        })