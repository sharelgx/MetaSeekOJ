# -*- coding: utf-8 -*-
"""
增强的专题管理API视图
"""

from django.db import transaction
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
from account.decorators import login_required, super_admin_required
from ..models import (
    Topic, TopicCategoryRelation, TopicTagRelation, TopicQuestion,
    TopicPracticeRecord, TopicWrongQuestionRecord, ChoiceQuestion,
    Category, QuestionTag
)
from .topic_serializers import (
    TopicListSerializer, TopicDetailSerializer, TopicCreateSerializer,
    TopicUpdateSerializer, TopicQuestionSerializer
)


class TopicManageAPI(CSRFExemptAPIView):
    """
    增强的专题管理API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取专题列表（增强版）
        """
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        keyword = request.GET.get('keyword', '').strip()
        category_id = request.GET.get('category_id')
        difficulty = request.GET.get('difficulty')
        is_active = request.GET.get('is_active')
        is_public = request.GET.get('is_public')
        created_by = request.GET.get('created_by')
        sort_by = request.GET.get('sort_by', '-create_time')
        
        # 构建查询条件
        queryset = Topic.objects.select_related('created_by').prefetch_related(
            'topic_categories__category',
            'topic_tags__tag',
            'topic_questions__question'
        )
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        # 分类筛选
        if category_id:
            topic_ids = TopicCategoryRelation.objects.filter(
                category_id=category_id
            ).values_list('topic_id', flat=True)
            queryset = queryset.filter(id__in=topic_ids)
        
        # 难度筛选
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # 状态筛选
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # 创建者筛选
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        # 排序
        valid_sort_fields = [
            'create_time', '-create_time', 'title', '-title',
            'difficulty_level', '-difficulty_level', 'total_questions', '-total_questions'
        ]
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-create_time')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        topics = queryset[start:end]
        
        # 序列化数据
        results = []
        for topic in topics:
            # 获取分类信息
            categories = []
            for rel in topic.topic_categories.all():
                categories.append({
                    'id': rel.category.id,
                    'name': rel.category.name,
                    'full_name': rel.category.get_full_name()
                })
            
            # 获取标签信息
            tags = []
            for rel in topic.topic_tags.all():
                tags.append({
                    'id': rel.tag.id,
                    'name': rel.tag.name
                })
            
            # 获取练习统计
            practice_count = TopicPracticeRecord.objects.filter(topic=topic).count()
            completed_count = TopicPracticeRecord.objects.filter(
                topic=topic, status='completed'
            ).count()
            
            results.append({
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'difficulty_level': topic.difficulty_level,
                'difficulty_text': topic.get_difficulty_level_display(),
                'cover_image': topic.cover_image,
                'is_public': topic.is_public,
                'is_active': topic.is_active,
                'pass_score': topic.pass_score,
                'total_questions': topic.total_questions,
                'created_by': topic.created_by.username if topic.created_by else None,
                'create_time': topic.create_time.strftime('%Y-%m-%d %H:%M:%S') if topic.create_time else None,
                'update_time': topic.last_update_time.strftime('%Y-%m-%d %H:%M:%S') if topic.last_update_time else None,
                'categories': categories,
                'tags': tags,
                'practice_count': practice_count,
                'completed_count': completed_count
            })
        
        return self.success({
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    
    @super_admin_required
    def post(self, request):
        """
        创建专题（增强版）
        """
        data = request.data
        
        with transaction.atomic():
            # 基础信息
            topic_data = {
                'title': data.get('title', '').strip(),
                'description': data.get('description', '').strip(),
                'difficulty_level': data.get('difficulty_level', 1),
                'cover_image': data.get('cover_image', ''),
                'is_public': data.get('is_public', True),
                'is_active': data.get('is_active', True),
                'pass_score': data.get('pass_score', 60),
                'created_by': request.user
            }
            
            # 验证基础信息
            if not topic_data['title']:
                return self.error("专题标题不能为空")
            
            if len(topic_data['title']) > 200:
                return self.error("专题标题不能超过200个字符")
            
            if Topic.objects.filter(title=topic_data['title']).exists():
                return self.error("专题标题已存在")
            
            if not (1 <= topic_data['difficulty_level'] <= 5):
                return self.error("难度等级必须在1-5之间")
            
            if not (0 <= topic_data['pass_score'] <= 100):
                return self.error("及格分数必须在0-100之间")
            
            # 创建专题
            topic = Topic.objects.create(**topic_data)
            
            # 处理分类关联
            category_ids = data.get('category_ids', [])
            if category_ids:
                categories = Category.objects.filter(id__in=category_ids, is_active=True)
                for category in categories:
                    TopicCategoryRelation.objects.create(
                        topic=topic,
                        category=category
                    )
            
            # 处理标签关联
            tag_ids = data.get('tag_ids', [])
            if tag_ids:
                tags = QuestionTag.objects.filter(id__in=tag_ids)
                for tag in tags:
                    TopicTagRelation.objects.create(
                        topic=topic,
                        tag=tag
                    )
            
            # 处理题目关联
            question_data = data.get('questions', [])
            if question_data:
                for item in question_data:
                    question_id = item.get('question_id')
                    order_index = item.get('order_index', 0)
                    
                    try:
                        question = ChoiceQuestion.objects.get(id=question_id, visible=True)
                        TopicQuestion.objects.create(
                            topic=topic,
                            question=question,
                            order_index=order_index
                        )
                    except ChoiceQuestion.DoesNotExist:
                        continue
            
            # 更新题目数量
            topic.update_question_count()
            
            # 返回详细信息
            return self.success({
                'id': topic.id,
                'title': topic.title,
                'message': '专题创建成功'
            })


class TopicDetailManageAPI(APIView):
    """
    专题详情管理API
    """
    
    @super_admin_required
    def get(self, request, topic_id):
        """
        获取专题详情（管理端）
        """
        try:
            topic = Topic.objects.select_related('created_by').prefetch_related(
                'topic_categories__category',
                'topic_tags__tag',
                'topic_questions__question'
            ).get(id=topic_id)
            
            # 基础信息
            data = {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'difficulty_level': topic.difficulty_level,
                'difficulty_text': topic.get_difficulty_level_display(),
                'cover_image': topic.cover_image,
                'is_public': topic.is_public,
                'is_active': topic.is_active,
                'pass_score': topic.pass_score,
                'total_questions': topic.total_questions,
                'created_by': topic.created_by.username if topic.created_by else None,
                'create_time': topic.create_time.strftime('%Y-%m-%d %H:%M:%S') if topic.create_time else None,
                'update_time': topic.last_update_time.strftime('%Y-%m-%d %H:%M:%S') if topic.last_update_time else None
            }
            
            # 分类信息
            categories = []
            for rel in topic.topic_categories.all():
                categories.append({
                    'id': rel.category.id,
                    'name': rel.category.name,
                    'full_name': rel.category.get_full_name()
                })
            data['categories'] = categories
            
            # 标签信息
            tags = []
            for rel in topic.topic_tags.all():
                tags.append({
                    'id': rel.tag.id,
                    'name': rel.tag.name
                })
            data['tags'] = tags
            
            # 题目信息
            questions = []
            for tq in topic.topic_questions.all().order_by('order_index'):
                questions.append({
                    'id': tq.question.id,
                    'title': tq.question.title,
                    'difficulty': tq.question.difficulty,
                    'score': tq.question.score,
                    'order_index': tq.order_index,
                    'question_type': tq.question.question_type,
                    'category_name': tq.question.category.name if tq.question.category else '',
                    'create_time': tq.question.create_time
                })
            data['questions'] = questions
            
            # 统计信息
            practice_stats = TopicPracticeRecord.objects.filter(topic=topic).aggregate(
                total_practices=Count('id'),
                completed_practices=Count('id', filter=Q(status='completed')),
                avg_score=Avg('score', filter=Q(status='completed'))
            )
            
            data['statistics'] = {
                'total_practices': practice_stats['total_practices'] or 0,
                'completed_practices': practice_stats['completed_practices'] or 0,
                'completion_rate': round(
                    (practice_stats['completed_practices'] or 0) / 
                    max(practice_stats['total_practices'] or 1, 1) * 100, 2
                ),
                'avg_score': round(practice_stats['avg_score'] or 0, 2),
                'unique_users': TopicPracticeRecord.objects.filter(
                    topic=topic
                ).values('user').distinct().count()
            }
            
            return self.success(data)
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def put(self, request, topic_id):
        """
        更新专题（增强版）
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            data = request.data
            
            with transaction.atomic():
                # 更新基础信息
                title = data.get('title', '').strip()
                if title and title != topic.title:
                    if Topic.objects.filter(title=title).exclude(id=topic.id).exists():
                        return self.error("专题标题已存在")
                    topic.title = title
                
                description = data.get('description', '').strip()
                if description is not None:
                    topic.description = description
                
                difficulty_level = data.get('difficulty_level')
                if difficulty_level is not None:
                    if not (1 <= difficulty_level <= 5):
                        return self.error("难度等级必须在1-5之间")
                    topic.difficulty_level = difficulty_level
                
                cover_image = data.get('cover_image')
                if cover_image is not None:
                    topic.cover_image = cover_image
                
                is_public = data.get('is_public')
                if is_public is not None:
                    topic.is_public = is_public
                
                is_active = data.get('is_active')
                if is_active is not None:
                    topic.is_active = is_active
                
                pass_score = data.get('pass_score')
                if pass_score is not None:
                    if not (0 <= pass_score <= 100):
                        return self.error("及格分数必须在0-100之间")
                    topic.pass_score = pass_score
                
                topic.save()
                
                # 更新分类关联
                category_ids = data.get('category_ids')
                if category_ids is not None:
                    # 删除现有关联
                    TopicCategoryRelation.objects.filter(topic=topic).delete()
                    # 创建新关联
                    if category_ids:
                        categories = Category.objects.filter(id__in=category_ids, is_active=True)
                        for category in categories:
                            TopicCategoryRelation.objects.create(
                                topic=topic,
                                category=category
                            )
                
                # 更新标签关联
                tag_ids = data.get('tag_ids')
                if tag_ids is not None:
                    # 删除现有关联
                    TopicTagRelation.objects.filter(topic=topic).delete()
                    # 创建新关联
                    if tag_ids:
                        tags = QuestionTag.objects.filter(id__in=tag_ids)
                        for tag in tags:
                            TopicTagRelation.objects.create(
                                topic=topic,
                                tag=tag
                            )
                
                # 更新题目关联
                question_data = data.get('questions')
                if question_data is not None:
                    # 删除现有关联
                    TopicQuestion.objects.filter(topic=topic).delete()
                    # 创建新关联
                    for item in question_data:
                        question_id = item.get('question_id')
                        order_index = item.get('order_index', 0)
                        
                        try:
                            question = ChoiceQuestion.objects.get(id=question_id, visible=True)
                            TopicQuestion.objects.create(
                                topic=topic,
                                question=question,
                                order_index=order_index
                            )
                        except ChoiceQuestion.DoesNotExist:
                            continue
                    
                    # 更新题目数量
                    topic.update_question_count()
                
                return self.success({
                    'id': topic.id,
                    'title': topic.title,
                    'message': '专题更新成功'
                })
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def delete(self, request, topic_id):
        """
        删除专题
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            
            # 检查是否有练习记录
            if TopicPracticeRecord.objects.filter(topic=topic).exists():
                return self.error("该专题已有用户练习记录，不能删除")
            
            topic.delete()
            return self.success("专题删除成功")
        except Topic.DoesNotExist:
            return self.error("专题不存在")


class TopicQuestionsManageAPI(APIView):
    """
    专题题目管理API
    """
    
    @super_admin_required
    def get(self, request, topic_id):
        """
        获取专题题目列表
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            
            # 获取已关联的题目
            topic_questions = TopicQuestion.objects.filter(
                topic=topic
            ).select_related('question').order_by('order_index')
            
            questions = []
            for tq in topic_questions:
                questions.append({
                    'id': tq.question.id,
                    'title': tq.question.title,
                    'difficulty': tq.question.difficulty,
                    'score': tq.question.score,
                    'order_index': tq.order_index,
                    'question_type': tq.question.question_type,
                    'category_name': tq.question.category.name if tq.question.category else '',
                    'create_time': tq.question.create_time
                })
            
            return self.success({
                'topic_id': topic.id,
                'topic_title': topic.title,
                'questions': questions,
                'total': len(questions)
            })
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def post(self, request, topic_id):
        """
        为专题添加题目
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            data = request.data
            question_ids = data.get('question_ids', [])
            
            if not question_ids:
                return self.error("请选择要添加的题目")
            
            # 验证题目是否存在
            questions = ChoiceQuestion.objects.filter(id__in=question_ids, visible=True)
            if questions.count() != len(question_ids):
                return self.error("部分题目不存在或已被删除")
            
            # 获取当前最大排序值
            max_order = TopicQuestion.objects.filter(topic=topic).aggregate(
                max_order=Count('order_index')
            )['max_order'] or 0
            
            # 批量添加题目
            added_count = 0
            for question in questions:
                relation, created = TopicQuestion.objects.get_or_create(
                    topic=topic,
                    question=question,
                    defaults={'order_index': max_order + added_count + 1}
                )
                if created:
                    added_count += 1
            
            # 更新题目数量
            topic.update_question_count()
            
            return self.success({
                'added_count': added_count,
                'total_count': len(question_ids),
                'message': f"成功添加 {added_count} 道题目"
            })
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def put(self, request, topic_id):
        """
        更新专题题目排序
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            data = request.data
            question_orders = data.get('question_orders', [])
            
            # 更新排序
            with transaction.atomic():
                for item in question_orders:
                    question_id = item.get('question_id')
                    order_index = item.get('order_index', 0)
                    
                    TopicQuestion.objects.filter(
                        topic=topic,
                        question_id=question_id
                    ).update(order_index=order_index)
            
            return self.success("题目排序更新成功")
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def delete(self, request, topic_id):
        """
        从专题中移除题目
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            data = request.data
            question_ids = data.get('question_ids', [])
            
            if not question_ids:
                return self.error("请选择要移除的题目")
            
            # 删除题目关联
            deleted_count = TopicQuestion.objects.filter(
                topic=topic,
                question_id__in=question_ids
            ).delete()[0]
            
            # 更新题目数量
            topic.update_question_count()
            
            return self.success({
                'removed_count': deleted_count,
                'message': f"成功移除 {deleted_count} 道题目"
            })
        except Topic.DoesNotExist:
            return self.error("专题不存在")


class TopicQuestionSelectorAPI(APIView):
    """
    题目选择器API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取可选择的题目列表
        """
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        keyword = request.GET.get('keyword', '').strip()
        category_id = request.GET.get('category_id')
        difficulty = request.GET.get('difficulty')
        exclude_topic_id = request.GET.get('exclude_topic_id')
        
        # 构建查询条件
        queryset = ChoiceQuestion.objects.filter(visible=True)
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        
        # 分类筛选
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 难度筛选
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # 排除已关联专题的题目
        if exclude_topic_id:
            exclude_question_ids = TopicQuestion.objects.filter(
                topic_id=exclude_topic_id
            ).values_list('question_id', flat=True)
            queryset = queryset.exclude(id__in=exclude_question_ids)
        
        # 排序
        queryset = queryset.order_by('-create_time')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        questions = queryset[start:end]
        
        # 序列化数据
        results = []
        for question in questions:
            results.append({
                'id': question.id,
                'title': question.title,
                'difficulty': question.difficulty,
                'score': question.score,
                'question_type': question.question_type,
                'category_name': question.category.name if question.category else '',
                'create_time': question.create_time
            })
        
        return self.success({
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })


class TopicBatchAPI(APIView):
    """
    专题批量操作API
    """
    
    @super_admin_required
    def post(self, request):
        """
        批量操作专题
        """
        data = request.data
        action = data.get('action')  # enable, disable, delete, change_category
        topic_ids = data.get('topic_ids', [])
        
        if not topic_ids:
            return self.error("请选择要操作的专题")
        
        topics = Topic.objects.filter(id__in=topic_ids)
        if not topics.exists():
            return self.error("未找到有效的专题")
        
        success_count = 0
        error_messages = []
        
        with transaction.atomic():
            for topic in topics:
                try:
                    if action == 'enable':
                        topic.is_active = True
                        topic.save()
                        success_count += 1
                    elif action == 'disable':
                        topic.is_active = False
                        topic.save()
                        success_count += 1
                    elif action == 'public':
                        topic.is_public = True
                        topic.save()
                        success_count += 1
                    elif action == 'private':
                        topic.is_public = False
                        topic.save()
                        success_count += 1
                    elif action == 'delete':
                        # 检查是否可以删除
                        if TopicPracticeRecord.objects.filter(topic=topic).exists():
                            error_messages.append(f"专题 '{topic.title}' 已有练习记录，不能删除")
                            continue
                        topic.delete()
                        success_count += 1
                    elif action == 'change_category':
                        category_ids = data.get('category_ids', [])
                        # 删除现有分类关联
                        TopicCategoryRelation.objects.filter(topic=topic).delete()
                        # 添加新分类关联
                        if category_ids:
                            categories = Category.objects.filter(id__in=category_ids, is_active=True)
                            for category in categories:
                                TopicCategoryRelation.objects.create(
                                    topic=topic,
                                    category=category
                                )
                        success_count += 1
                    else:
                        error_messages.append(f"未知操作: {action}")
                except Exception as e:
                    error_messages.append(f"处理专题 '{topic.title}' 时出错: {str(e)}")
        
        if success_count == len(topic_ids):
            result = {
                'success_count': success_count,
                'total_count': len(topic_ids),
                'error_messages': error_messages,
                'message': '批量操作完成'
            }
            return self.success(result)
        elif success_count > 0:
            result = {
                'success_count': success_count,
                'total_count': len(topic_ids),
                'error_messages': error_messages,
                'message': f'部分操作成功，成功处理 {success_count} 个专题'
            }
            return self.success(result)
        else:
            result = {
                'success_count': success_count,
                'total_count': len(topic_ids),
                'error_messages': error_messages
            }
            return self.error("批量操作失败", result)
