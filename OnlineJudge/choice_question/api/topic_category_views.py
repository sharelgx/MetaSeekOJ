# -*- coding: utf-8 -*-
"""
专题分类管理API视图
"""

from django.db.models import Q, Count
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
from account.decorators import super_admin_required
from ..models import Category, Topic, TopicCategoryRelation
from .topic_serializers import TopicCategorySerializer, TopicCategoryDetailSerializer


class TopicCategoryListAPI(CSRFExemptAPIView):
    """
    专题分类列表API
    """
    
    def get(self, request):
        """
        获取专题分类列表（树形结构）
        """
        # 获取查询参数
        include_inactive = request.GET.get('include_inactive', 'false').lower() == 'true'
        parent_id = request.GET.get('parent_id', None)
        level = request.GET.get('level', None)
        
        # 构建查询条件
        queryset = Category.objects.all()
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        if parent_id is not None:
            if parent_id == '':
                # 获取根分类
                queryset = queryset.filter(parent=None)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        if level is not None:
            queryset = queryset.filter(level=level)
        
        # 排序
        queryset = queryset.order_by('tree_id', 'lft')
        
        # 序列化
        serializer = TopicCategorySerializer(queryset, many=True)
        return self.success(serializer.data)
    
    @super_admin_required
    def post(self, request):
        """
        创建专题分类
        """
        data = request.data
        name = data.get('name', '').strip()
        parent_id = data.get('parent_id', None)
        description = data.get('description', '').strip()
        order = data.get('order', 0)
        is_active = data.get('is_active', True)
        
        # 验证参数
        if not name:
            return self.error("分类名称不能为空")
        
        if len(name) > 100:
            return self.error("分类名称不能超过100个字符")
        
        # 检查父分类
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id, is_active=True)
            except Category.DoesNotExist:
                return self.error("父分类不存在")
        
        # 检查同级分类名称重复
        sibling_query = Category.objects.filter(parent=parent, name=name)
        if sibling_query.exists():
            return self.error("同级分类中已存在相同名称的分类")
        
        # 创建分类
        category = Category.objects.create(
            name=name,
            parent=parent,
            description=description,
            order=order,
            is_active=is_active
        )
        
        # 更新题目数量
        category.update_question_count()
        
        serializer = TopicCategoryDetailSerializer(category)
        return self.success(serializer.data)


class TopicCategoryDetailAPI(APIView):
    """
    专题分类详情API
    """
    
    def get(self, request, category_id):
        """
        获取分类详情
        """
        try:
            category = Category.objects.get(id=category_id)
            serializer = TopicCategoryDetailSerializer(category)
            return self.success(serializer.data)
        except Category.DoesNotExist:
            return self.error("分类不存在")
    
    @super_admin_required
    def put(self, request, category_id):
        """
        更新分类
        """
        try:
            category = Category.objects.get(id=category_id)
            data = request.data
            
            name = data.get('name', '').strip()
            parent_id = data.get('parent_id', None)
            description = data.get('description', '').strip()
            order = data.get('order', category.order)
            is_active = data.get('is_active', category.is_active)
            
            # 验证参数
            if not name:
                return self.error("分类名称不能为空")
            
            if len(name) > 100:
                return self.error("分类名称不能超过100个字符")
            
            # 检查父分类
            parent = None
            if parent_id:
                try:
                    parent = Category.objects.get(id=parent_id, is_active=True)
                    # 检查不能设置自己或子分类为父分类
                    if parent.pk == category.pk or parent in category.get_descendants():
                        return self.error("不能设置自己或子分类为父分类")
                except Category.DoesNotExist:
                    return self.error("父分类不存在")
            
            # 检查同级分类名称重复（排除自己）
            sibling_query = Category.objects.filter(
                parent=parent, name=name
            ).exclude(id=category.id)
            if sibling_query.exists():
                return self.error("同级分类中已存在相同名称的分类")
            
            # 更新分类
            category.name = name
            category.parent = parent
            category.description = description
            category.order = order
            category.is_active = is_active
            category.save()
            
            # 更新题目数量
            category.update_question_count()
            
            serializer = TopicCategoryDetailSerializer(category)
            return self.success(serializer.data)
        except Category.DoesNotExist:
            return self.error("分类不存在")
    
    @super_admin_required
    def delete(self, request, category_id):
        """
        删除分类
        """
        try:
            category = Category.objects.get(id=category_id)
            
            # 检查是否有子分类
            if category.get_children().exists():
                return self.error("该分类下还有子分类，不能删除")
            
            # 检查是否有关联的专题
            if TopicCategoryRelation.objects.filter(category=category).exists():
                return self.error("该分类下还有关联的专题，不能删除")
            
            category.delete()
            return self.success("删除成功")
        except Category.DoesNotExist:
            return self.error("分类不存在")


class TopicCategoryTreeAPI(APIView):
    """
    专题分类树API
    """
    
    def get(self, request):
        """
        获取完整的分类树
        """
        include_inactive = request.GET.get('include_inactive', 'false').lower() == 'true'
        include_topic_count = request.GET.get('include_topic_count', 'false').lower() == 'true'
        
        # 获取根分类
        queryset = Category.objects.filter(parent=None)
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        queryset = queryset.order_by('order', 'name')
        
        def build_tree(categories):
            tree = []
            for category in categories:
                # 构建节点数据
                node = {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'order': category.order,
                    'is_active': category.is_active,
                    'level': category.level,
                    'full_name': category.get_full_name(),
                    'question_count': category.question_count
                }
                
                # 添加专题数量统计
                if include_topic_count:
                    topic_count = TopicCategoryRelation.objects.filter(
                        category=category
                    ).count()
                    node['topic_count'] = topic_count
                
                # 递归获取子分类
                children = category.get_children()
                if not include_inactive:
                    children = children.filter(is_active=True)
                children = children.order_by('order', 'name')
                
                if children.exists():
                    node['children'] = build_tree(children)
                else:
                    node['children'] = []
                
                tree.append(node)
            
            return tree
        
        tree_data = build_tree(queryset)
        return self.success(tree_data)


class TopicCategoryMoveAPI(APIView):
    """
    专题分类移动API
    """
    
    @super_admin_required
    def post(self, request):
        """
        移动分类到新的父分类下
        """
        data = request.data
        category_id = data.get('category_id')
        target_parent_id = data.get('target_parent_id', None)
        position = data.get('position', 'last')  # first, last, left, right
        reference_id = data.get('reference_id', None)  # 参考节点ID
        
        try:
            category = Category.objects.get(id=category_id)
            
            # 检查目标父分类
            target_parent = None
            if target_parent_id:
                try:
                    target_parent = Category.objects.get(id=target_parent_id)
                    # 检查不能移动到自己或子分类下
                    if target_parent.pk == category.pk or target_parent in category.get_descendants():
                        return self.error("不能移动到自己或子分类下")
                except Category.DoesNotExist:
                    return self.error("目标父分类不存在")
            
            # 执行移动操作
            if position == 'first':
                category.move_to(target_parent, position='first-child')
            elif position == 'last':
                category.move_to(target_parent, position='last-child')
            elif position == 'left' and reference_id:
                try:
                    reference = Category.objects.get(id=reference_id)
                    category.move_to(reference, position='left')
                except Category.DoesNotExist:
                    return self.error("参考节点不存在")
            elif position == 'right' and reference_id:
                try:
                    reference = Category.objects.get(id=reference_id)
                    category.move_to(reference, position='right')
                except Category.DoesNotExist:
                    return self.error("参考节点不存在")
            else:
                category.move_to(target_parent, position='last-child')
            
            return self.success("移动成功")
        except Category.DoesNotExist:
            return self.error("分类不存在")


class TopicCategoryBatchAPI(APIView):
    """
    专题分类批量操作API
    """
    
    @super_admin_required
    def post(self, request):
        """
        批量操作分类
        """
        data = request.data
        action = data.get('action')  # enable, disable, delete
        category_ids = data.get('category_ids', [])
        
        if not category_ids:
            return self.error("请选择要操作的分类")
        
        categories = Category.objects.filter(id__in=category_ids)
        if not categories.exists():
            return self.error("未找到有效的分类")
        
        success_count = 0
        error_messages = []
        
        for category in categories:
            try:
                if action == 'enable':
                    category.is_active = True
                    category.save()
                    success_count += 1
                elif action == 'disable':
                    category.is_active = False
                    category.save()
                    success_count += 1
                elif action == 'delete':
                    # 检查是否可以删除
                    if category.get_children().exists():
                        error_messages.append(f"分类 '{category.name}' 下还有子分类，不能删除")
                        continue
                    if TopicCategoryRelation.objects.filter(category=category).exists():
                        error_messages.append(f"分类 '{category.name}' 下还有关联的专题，不能删除")
                        continue
                    category.delete()
                    success_count += 1
                else:
                    error_messages.append(f"未知操作: {action}")
            except Exception as e:
                error_messages.append(f"处理分类 '{category.name}' 时出错: {str(e)}")
        
        result = {
            'success_count': success_count,
            'total_count': len(category_ids),
            'error_messages': error_messages
        }
        
        if success_count == len(category_ids):
            return self.success(result, "批量操作完成")
        elif success_count > 0:
            return self.success(result, f"部分操作成功，成功处理 {success_count} 个分类")
        else:
            return self.error("批量操作失败", result)


class TopicCategoryTopicsAPI(APIView):
    """
    分类关联专题API
    """
    
    def get(self, request, category_id):
        """
        获取分类下的专题列表
        """
        try:
            category = Category.objects.get(id=category_id)
            
            # 获取分类关联的专题
            topic_relations = TopicCategoryRelation.objects.filter(
                category=category
            ).select_related('topic')
            
            topics = []
            for relation in topic_relations:
                topic = relation.topic
                topics.append({
                    'id': topic.id,
                    'title': topic.title,
                    'description': topic.description,
                    'difficulty_level': topic.difficulty_level,
                    'total_questions': topic.total_questions,
                    'is_active': topic.is_active,
                    'is_public': topic.is_public,
                    'create_time': topic.create_time,
                    'created_by': topic.created_by.username if topic.created_by else None
                })
            
            return self.success({
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'full_name': category.get_full_name(),
                    'description': category.description
                },
                'topics': topics,
                'total': len(topics)
            })
        except Category.DoesNotExist:
            return self.error("分类不存在")
    
    @super_admin_required
    def post(self, request, category_id):
        """
        为分类添加专题
        """
        try:
            category = Category.objects.get(id=category_id)
            data = request.data
            topic_ids = data.get('topic_ids', [])
            
            if not topic_ids:
                return self.error("请选择要添加的专题")
            
            # 验证专题是否存在
            topics = Topic.objects.filter(id__in=topic_ids)
            if topics.count() != len(topic_ids):
                return self.error("部分专题不存在")
            
            # 批量创建关联关系
            relations = []
            for topic in topics:
                relation, created = TopicCategoryRelation.objects.get_or_create(
                    topic=topic,
                    category=category
                )
                if created:
                    relations.append(relation)
            
            return self.success({
                'added_count': len(relations),
                'total_count': len(topic_ids),
                'message': f"成功添加 {len(relations)} 个专题到分类"
            })
        except Category.DoesNotExist:
            return self.error("分类不存在")
    
    @super_admin_required
    def delete(self, request, category_id):
        """
        从分类中移除专题
        """
        try:
            category = Category.objects.get(id=category_id)
            data = request.data
            topic_ids = data.get('topic_ids', [])
            
            if not topic_ids:
                return self.error("请选择要移除的专题")
            
            # 删除关联关系
            deleted_count = TopicCategoryRelation.objects.filter(
                category=category,
                topic_id__in=topic_ids
            ).delete()[0]
            
            return self.success({
                'removed_count': deleted_count,
                'message': f"成功从分类中移除 {deleted_count} 个专题"
            })
        except Category.DoesNotExist:
            return self.error("分类不存在")
