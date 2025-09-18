# -*- coding: utf-8 -*-
"""
选择题标签API视图
"""

from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView, validate_serializer
# from utils.api._serializers import PaginationSerializer  # PaginationSerializer不存在
# from utils.shortcuts import paginate_data  # 使用APIView的paginate_data方法
from account.decorators import super_admin_required
from ..models import QuestionTag
from ..serializers import ChoiceQuestionTagSerializer


class QuestionTagAPI(APIView):
    """
    题目标签API
    """
    
    # @validate_serializer(PaginationSerializer)  # PaginationSerializer不存在
    def get(self, request):
        """
        获取标签列表
        """
        # 获取查询参数
        tag_type = request.GET.get('tag_type')
        active_only = request.GET.get('active_only', 'true').lower() == 'true'
        popular = request.GET.get('popular', 'false').lower() == 'true'
        
        # 构建查询条件
        queryset = QuestionTag.objects.all()
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        if tag_type and tag_type in ['difficulty', 'subject', 'knowledge', 'custom']:
            queryset = queryset.filter(tag_type=tag_type)
        
        if popular:
            # 获取热门标签（按题目数量排序）
            queryset = queryset.filter(question_count__gt=0).order_by('-question_count')[:20]
            return self.success(ChoiceQuestionTagSerializer(queryset, many=True).data)
        
        return self.success(self.paginate_data(request, queryset, ChoiceQuestionTagSerializer))
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionTagSerializer)
    def post(self, request):
        """
        创建标签
        """
        serializer = ChoiceQuestionTagSerializer(data=request.data)
        if serializer.is_valid():
            tag = serializer.save()
            return self.success(ChoiceQuestionTagSerializer(tag).data)
        return self.error(serializer.errors)


class QuestionTagDetailAPI(APIView):
    """
    标签详情API
    """
    
    def get(self, request, tag_id):
        """
        获取标签详情
        """
        try:
            tag = QuestionTag.objects.get(id=tag_id)
            return self.success(ChoiceQuestionTagSerializer(tag).data)
        except QuestionTag.DoesNotExist:
            return self.error("标签不存在", status_code=404)
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionTagSerializer)
    def put(self, request, tag_id):
        """
        更新标签
        """
        try:
            tag = QuestionTag.objects.get(id=tag_id)
        except QuestionTag.DoesNotExist:
            return self.error("标签不存在", status_code=404)
        
        serializer = ChoiceQuestionTagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            tag = serializer.save()
            # 更新题目数量统计
            tag.update_question_count()
            return self.success(ChoiceQuestionTagSerializer(tag).data)
        return self.error(serializer.errors)
    
    @super_admin_required
    def delete(self, request, tag_id):
        """
        删除标签
        """
        try:
            tag = QuestionTag.objects.get(id=tag_id)
        except QuestionTag.DoesNotExist:
            return self.error("标签不存在", status_code=404)
        
        # 检查是否有关联的题目
        if tag.choicequestion_set.exists():
            return self.error("该标签下还有题目，请先移除题目的标签关联")
        
        tag.delete()
        return self.success("删除成功")


class QuestionTagBatchAPI(APIView):
    """
    标签批量操作API
    """
    
    @super_admin_required
    def post(self, request):
        """
        批量操作标签
        """
        action = request.data.get('action')  # activate, deactivate, delete, update_type
        tag_ids = request.data.get('tag_ids', [])
        
        if not action or not tag_ids:
            return self.error("请指定操作类型和标签ID列表")
        
        tags = QuestionTag.objects.filter(id__in=tag_ids)
        
        if not tags.exists():
            return self.error("未找到有效的标签")
        
        success_count = 0
        
        if action == 'activate':
            success_count = tags.update(is_active=True)
        
        elif action == 'deactivate':
            success_count = tags.update(is_active=False)
        
        elif action == 'delete':
            # 检查是否有关联的题目
            for tag in tags:
                if tag.choicequestion_set.exists():
                    return self.error(f"标签 '{tag.name}' 下还有题目，无法删除")
            
            success_count = tags.count()
            tags.delete()
        
        elif action == 'update_type':
            tag_type = request.data.get('tag_type')
            if tag_type not in ['difficulty', 'subject', 'knowledge', 'custom']:
                return self.error("无效的标签类型")
            
            success_count = tags.update(tag_type=tag_type)
        
        else:
            return self.error("无效的操作类型")
        
        return self.success(f"成功处理 {success_count} 个标签")


class QuestionTagStatisticsAPI(APIView):
    """
    标签统计API
    """
    
    def get(self, request):
        """
        获取标签统计信息
        """
        # 总体统计
        total_tags = QuestionTag.objects.count()
        active_tags = QuestionTag.objects.filter(is_active=True).count()
        
        # 按类型统计
        type_stats = {}
        for tag_type, tag_type_name in QuestionTag.TAG_TYPE_CHOICES:
            type_stats[tag_type] = {
                'name': tag_type_name,
                'count': QuestionTag.objects.filter(tag_type=tag_type).count(),
                'active_count': QuestionTag.objects.filter(tag_type=tag_type, is_active=True).count()
            }
        
        # 热门标签
        popular_tags = QuestionTag.get_popular_tags(limit=10)
        
        # 未使用的标签
        unused_tags = QuestionTag.objects.filter(question_count=0).count()
        
        statistics = {
            'total_tags': total_tags,
            'active_tags': active_tags,
            'inactive_tags': total_tags - active_tags,
            'unused_tags': unused_tags,
            'type_distribution': type_stats,
            'popular_tags': QuestionTagSerializer(popular_tags, many=True).data
        }
        
        return self.success(statistics)