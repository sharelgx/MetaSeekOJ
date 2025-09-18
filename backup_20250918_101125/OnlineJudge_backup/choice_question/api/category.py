# -*- coding: utf-8 -*-
"""
选择题分类API视图
"""

from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView, validate_serializer
from account.decorators import super_admin_required
from ..models import Category
from ..serializers import ChoiceQuestionCategorySerializer


class CategoryAPI(APIView):
    """
    分类API
    """
    
    def get(self, request):
        """
        获取分类列表（树形结构）
        """
        # 获取查询参数
        flat = request.GET.get('flat', 'false').lower() == 'true'
        active_only = request.GET.get('active_only', 'true').lower() == 'true'
        
        # 构建查询条件
        queryset = Category.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        if flat:
            # 扁平化列表
            categories = queryset.order_by('tree_id', 'lft')
            return self.success(ChoiceQuestionCategorySerializer(categories, many=True).data)
        else:
            # 树形结构 - 返回根分类及其所有子分类
            root_categories = queryset.filter(parent=None).order_by('order', 'name')
            serializer = ChoiceQuestionCategorySerializer(root_categories, many=True)
            return self.success(serializer.data)
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionCategorySerializer)
    def post(self, request):
        """
        创建分类
        """
        serializer = ChoiceQuestionCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        return self.error(serializer.errors)


class CategoryDetailAPI(APIView):
    """
    分类详情API
    """
    
    def get(self, request, category_id):
        """
        获取分类详情
        """
        try:
            category = Category.objects.get(id=category_id)
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        except Category.DoesNotExist:
            return self.error("分类不存在", status_code=404)
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionCategorySerializer)
    def put(self, request, category_id):
        """
        更新分类
        """
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.error("分类不存在", status_code=404)
        
        # 检查是否试图将分类设置为自己的子分类
        parent_id = request.data.get('parent')
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                if parent.is_descendant_of(category) or parent == category:
                    return self.error("不能将分类设置为自己或子分类的子分类")
            except Category.DoesNotExist:
                return self.error("父分类不存在")
        
        serializer = ChoiceQuestionCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            # 更新题目数量统计
            category.update_question_count()
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        return self.error(serializer.errors)
    
    @super_admin_required
    def delete(self, request, category_id):
        """
        删除分类
        """
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.error("分类不存在", status_code=404)
        
        # 检查是否有子分类
        if category.get_children().exists():
            return self.error("该分类下还有子分类，请先删除子分类")
        
        # 检查是否有关联的题目
        if category.choicequestion_set.exists():
            return self.error("该分类下还有题目，请先移动或删除题目")
        
        category.delete()
        return self.success("删除成功")


class CategoryMoveAPI(APIView):
    """
    分类移动API
    """
    
    @super_admin_required
    def post(self, request, category_id):
        """
        移动分类
        """
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.error("分类不存在", status_code=404)
        
        target_id = request.data.get('target_id')
        position = request.data.get('position', 'inside')  # inside, before, after
        
        if not target_id:
            return self.error("请指定目标分类")
        
        try:
            target = Category.objects.get(id=target_id)
        except Category.DoesNotExist:
            return self.error("目标分类不存在")
        
        # 检查是否试图移动到自己或子分类
        if target.is_descendant_of(category) or target == category:
            return self.error("不能移动到自己或子分类")
        
        try:
            if position == 'inside':
                category.move_to(target, 'last-child')
            elif position == 'before':
                category.move_to(target, 'left')
            elif position == 'after':
                category.move_to(target, 'right')
            else:
                return self.error("无效的移动位置")
            
            return self.success("移动成功")
        except Exception as e:
            return self.error(f"移动失败: {str(e)}")


class CategoryStatisticsAPI(APIView):
    """
    分类统计API
    """
    
    def get(self, request, category_id):
        """
        获取分类统计信息
        """
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.error("分类不存在", status_code=404)
        
        # 获取分类及其子分类的所有题目
        descendants = category.get_descendants(include_self=True)
        questions = category.get_all_questions()
        
        statistics = {
            'category_info': CategorySerializer(category).data,
            'total_questions': questions.count(),
            'difficulty_distribution': {
                'easy': questions.filter(difficulty='easy').count(),
                'medium': questions.filter(difficulty='medium').count(),
                'hard': questions.filter(difficulty='hard').count(),
            },
            'type_distribution': {
                'single': questions.filter(question_type='single').count(),
                'multiple': questions.filter(question_type='multiple').count(),
            },
            'subcategories_count': category.get_children().count(),
            'total_submissions': sum(q.total_submit for q in questions),
            'total_accepted': sum(q.total_accepted for q in questions),
        }
        
        # 计算平均正确率
        if statistics['total_submissions'] > 0:
            statistics['average_acceptance_rate'] = round(
                statistics['total_accepted'] / statistics['total_submissions'] * 100, 2
            )
        else:
            statistics['average_acceptance_rate'] = 0
        
        return self.success(statistics)