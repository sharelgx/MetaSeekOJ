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
    
    @super_admin_required
    def patch(self, request):
        """批量操作选择题"""
        try:
            action = request.data.get('action')
            question_ids = request.data.get('question_ids', [])
            
            if not action:
                return self.error("操作类型不能为空")
            
            if not question_ids:
                return self.error("题目ID列表不能为空")
            
            # 获取要操作的题目
            questions = ChoiceQuestion.objects.filter(id__in=question_ids)
            
            if not questions.exists():
                return self.error("未找到有效的题目")
            
            success_count = 0
            
            if action == 'delete':
                # 批量删除
                success_count = questions.count()
                questions.delete()
                
            elif action == 'toggle_visible':
                # 批量切换可见性
                for question in questions:
                    question.visible = not question.visible
                    question.save()
                    success_count += 1
                    
            elif action == 'set_visible':
                # 批量设置可见
                visible = request.data.get('visible', True)
                success_count = questions.update(visible=visible)
                
            elif action == 'set_difficulty':
                # 批量设置难度
                difficulty = request.data.get('difficulty')
                if difficulty not in ['easy', 'medium', 'hard']:
                    return self.error("无效的难度级别")
                success_count = questions.update(difficulty=difficulty)
                
            elif action == 'set_category':
                # 批量设置分类
                category_id = request.data.get('category_id')
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                        success_count = questions.update(category=category)
                    except Category.DoesNotExist:
                        return self.error("分类不存在")
                else:
                    success_count = questions.update(category=None)
                    
            else:
                return self.error(f"不支持的操作类型: {action}")
            
            return self.success({
                'message': f'成功处理 {success_count} 道题目',
                'success_count': success_count
            })
            
        except Exception as e:
            return self.error(f"批量操作失败: {str(e)}")


class ChoiceQuestionCategoryAdminAPI(APIView):
    """选择题分类管理员API"""
    
    @problem_permission_required
    def get(self, request):
        """获取分类列表或详情"""
        category_id = request.GET.get("id")
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                return self.success(ChoiceQuestionCategorySerializer(category).data)
            except Category.DoesNotExist:
                return self.error("Category does not exist")
        
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
    
    @problem_permission_required
    def put(self, request):
        """更新分类"""
        category_id = request.GET.get("id")
        if not category_id:
            return self.error("Category ID required")
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.error("Category does not exist")
        
        serializer = ChoiceQuestionCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        return self.error(serializer.errors)
    
    @super_admin_required
    def delete(self, request):
        """删除分类"""
        category_id = request.GET.get("id")
        if not category_id:
            return self.error("Category ID required")
        
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return self.success("删除成功")
        except Category.DoesNotExist:
            return self.error("Category does not exist")


class ChoiceQuestionTagAdminAPI(APIView):
    """选择题标签管理员API"""
    
    @problem_permission_required
    def get(self, request):
        """获取标签列表或详情"""
        tag_id = request.GET.get("id")
        if tag_id:
            try:
                tag = QuestionTag.objects.get(id=tag_id)
                return self.success(ChoiceQuestionTagSerializer(tag).data)
            except QuestionTag.DoesNotExist:
                return self.error("Tag does not exist")
        
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
    
    @problem_permission_required
    def put(self, request):
        """更新标签"""
        tag_id = request.GET.get("id")
        if not tag_id:
            return self.error("Tag ID required")
        
        try:
            tag = QuestionTag.objects.get(id=tag_id)
        except QuestionTag.DoesNotExist:
            return self.error("Tag does not exist")
        
        serializer = ChoiceQuestionTagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            tag = serializer.save()
            return self.success(ChoiceQuestionTagSerializer(tag).data)
        return self.error(serializer.errors)
    
    @super_admin_required
    def delete(self, request):
        """删除标签"""
        tag_id = request.GET.get("id")
        if not tag_id:
            return self.error("Tag ID required")
        
        try:
            tag = QuestionTag.objects.get(id=tag_id)
            tag.delete()
            return self.success("删除成功")
        except QuestionTag.DoesNotExist:
            return self.error("Tag does not exist")