# -*- coding: utf-8 -*-
"""
选择题管理员API视图
"""

from django.db.models import Q
from utils.api import APIView, validate_serializer
from account.decorators import problem_permission_required, super_admin_required
from .models import ChoiceQuestion, Category, QuestionTag
from .serializers import (
    ChoiceQuestionDetailSerializer,
    ChoiceQuestionCreateSerializer,
    ChoiceQuestionCategorySerializer,
    ChoiceQuestionTagSerializer
)


class ChoiceQuestionAdminAPI(APIView):
    """选择题管理员API"""
    
    @problem_permission_required
    def get(self, request):
        """获取选择题列表或详情"""
        question_id = request.GET.get("id")
        if question_id:
            try:
                question = ChoiceQuestion.objects.get(id=question_id)
                return self.success(ChoiceQuestionDetailSerializer(question).data)
            except ChoiceQuestion.DoesNotExist:
                return self.error("Question does not exist")
        
        # 列表查询
        questions = ChoiceQuestion.objects.all().order_by("-create_time")
        
        # 搜索过滤
        keyword = request.GET.get("keyword")
        if keyword:
            questions = questions.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword) |
                Q(_id__icontains=keyword)
            )
        
        # 分类过滤
        category_id = request.GET.get("category_id")
        if category_id:
            questions = questions.filter(category_id=category_id)
        
        # 难度过滤
        difficulty = request.GET.get("difficulty")
        if difficulty:
            questions = questions.filter(difficulty=difficulty)
        
        # 可见性过滤
        visible = request.GET.get("visible")
        if visible is not None:
            questions = questions.filter(visible=visible.lower() == 'true')
        
        # 分页
        if request.GET.get("paging") == "true":
            return self.success(self.paginate_data(request, questions, ChoiceQuestionDetailSerializer))
        
        return self.success(ChoiceQuestionDetailSerializer(questions, many=True).data)
    
    @problem_permission_required
    @validate_serializer(ChoiceQuestionCreateSerializer)
    def post(self, request):
        """创建选择题"""
        data = request.data
        
        # 生成显示ID
        if not data.get('_id'):
            # 获取最大的数字ID
            max_id = ChoiceQuestion.objects.filter(
                _id__regex=r'^[0-9]+$'
            ).extra(
                select={'id_as_int': 'CAST(_id AS UNSIGNED)'}
            ).order_by('-id_as_int').first()
            
            if max_id:
                next_id = int(max_id._id) + 1
            else:
                next_id = 1000
            data['_id'] = str(next_id)
        
        # 处理分类
        category_id = data.pop('category_id', None)
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                data['category'] = category
            except Category.DoesNotExist:
                return self.error("Category does not exist")
        
        # 处理标签
        tag_ids = data.pop('tag_ids', [])
        
        # 创建题目
        question = ChoiceQuestion.objects.create(
            created_by=request.user,
            **data
        )
        
        # 设置标签
        if tag_ids:
            tags = QuestionTag.objects.filter(id__in=tag_ids)
            question.tags.set(tags)
        
        return self.success(ChoiceQuestionDetailSerializer(question).data)
    
    @problem_permission_required
    def put(self, request):
        """更新选择题"""
        question_id = request.data.get("id")
        if not question_id:
            return self.error("Question ID required")
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return self.error("Question does not exist")
        
        data = request.data.copy()
        data.pop('id', None)  # 移除ID字段
        
        # 处理分类
        category_id = data.pop('category_id', None)
        if category_id is not None:
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    question.category = category
                except Category.DoesNotExist:
                    return self.error("Category does not exist")
            else:
                question.category = None
        
        # 处理标签
        tag_ids = data.pop('tag_ids', None)
        if tag_ids is not None:
            tags = QuestionTag.objects.filter(id__in=tag_ids)
            question.tags.set(tags)
        
        # 更新其他字段
        for attr, value in data.items():
            if hasattr(question, attr):
                setattr(question, attr, value)
        
        question.save()
        return self.success(ChoiceQuestionDetailSerializer(question).data)
    
    @super_admin_required
    def delete(self, request):
        """删除选择题"""
        question_id = request.GET.get("id")
        if not question_id:
            return self.error("Question ID required")
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
            question.delete()
            return self.success()
        except ChoiceQuestion.DoesNotExist:
            return self.error("Question does not exist")


class ChoiceQuestionCategoryAdminAPI(APIView):
    """选择题分类管理员API"""
    
    @problem_permission_required
    def get(self, request):
        """获取分类列表"""
        categories = Category.objects.all().order_by('name')
        return self.success(ChoiceQuestionCategorySerializer(categories, many=True).data)
    
    @problem_permission_required
    def post(self, request):
        """创建分类"""
        serializer = ChoiceQuestionCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        return self.error(serializer.errors)


class ChoiceQuestionTagAdminAPI(APIView):
    """选择题标签管理员API"""
    
    @problem_permission_required
    def get(self, request):
        """获取标签列表"""
        tags = QuestionTag.objects.all().order_by('name')
        return self.success(ChoiceQuestionTagSerializer(tags, many=True).data)
    
    @problem_permission_required
    def post(self, request):
        """创建标签"""
        serializer = ChoiceQuestionTagSerializer(data=request.data)
        if serializer.is_valid():
            tag = serializer.save()
            return self.success(ChoiceQuestionTagSerializer(tag).data)
        return self.error(serializer.errors)