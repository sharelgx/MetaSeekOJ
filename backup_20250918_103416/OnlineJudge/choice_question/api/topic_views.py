# -*- coding: utf-8 -*-
"""
专题功能API视图
"""

from django.db.models import Q, Count, Avg
from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.api import APIView, CSRFExemptAPIView, validate_serializer
from account.decorators import login_required, super_admin_required
from ..models import (
    Topic, TopicCategoryRelation, TopicTagRelation, TopicQuestion,
    TopicPracticeRecord, TopicWrongQuestionRecord, ChoiceQuestion,
    Category, QuestionTag, WrongQuestion
)
from .topic_serializers import (
    TopicListSerializer, TopicDetailSerializer, TopicCreateSerializer,
    TopicUpdateSerializer, TopicPracticeRecordSerializer,
    TopicPracticeSubmitSerializer, TopicWrongQuestionRecordSerializer,
    WrongQuestionStatisticsSerializer
)
from ..utils.judge import ChoiceQuestionJudge


class TopicAPI(CSRFExemptAPIView):
    """
    专题管理API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取专题列表
        """
        # 获取查询参数
        category_id = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        tag_ids = request.GET.get('tags', '').split(',') if request.GET.get('tags') else []
        keyword = request.GET.get('keyword', '').strip()
        is_public = request.GET.get('is_public')
        is_active = request.GET.get('is_active')
        created_by = request.GET.get('created_by')
        
        # 构建查询条件
        queryset = Topic.objects.all()
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        
        # 难度筛选
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # 公开状态筛选
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # 激活状态筛选
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 创建者筛选
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        # 分类筛选
        if category_id:
            topic_ids = TopicCategoryRelation.objects.filter(
                category_id=category_id
            ).values_list('topic_id', flat=True)
            queryset = queryset.filter(id__in=topic_ids)
        
        # 标签筛选
        if tag_ids and tag_ids != ['']:
            topic_ids = TopicTagRelation.objects.filter(
                tag_id__in=tag_ids
            ).values_list('topic_id', flat=True)
            queryset = queryset.filter(id__in=topic_ids)
        
        # 排序
        order_by = request.GET.get('order_by', '-create_time')
        if order_by in ['create_time', '-create_time', 'title', '-title', 'difficulty_level', '-difficulty_level']:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('-create_time')
        
        # 分页
        page_data = self.paginate_data(request, queryset, TopicListSerializer)
        return self.success(page_data)
    
    @super_admin_required
    @validate_serializer(TopicCreateSerializer)
    def post(self, request):
        """
        创建专题
        """
        serializer = TopicCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            topic = serializer.save()
            return self.success(TopicDetailSerializer(topic).data)
        return self.error("参数错误", serializer.errors)


class TopicDetailAPI(APIView):
    """
    专题详情API
    """
    
    def get(self, request, topic_id):
        """
        获取专题详情
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            
            # 检查权限
            if not topic.is_public and not request.user.is_authenticated:
                return self.error("专题不存在或无权限访问")
            
            if not topic.is_public and topic.created_by != request.user and not request.user.is_super_admin:
                return self.error("专题不存在或无权限访问")
            
            serializer = TopicDetailSerializer(topic)
            return self.success(serializer.data)
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    @validate_serializer(TopicUpdateSerializer)
    def put(self, request, topic_id):
        """
        更新专题
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            serializer = TopicUpdateSerializer(topic, data=request.data, partial=True)
            if serializer.is_valid():
                topic = serializer.save()
                return self.success(TopicDetailSerializer(topic).data)
            return self.error("参数错误", serializer.errors)
        except Topic.DoesNotExist:
            return self.error("专题不存在")
    
    @super_admin_required
    def delete(self, request, topic_id):
        """
        删除专题
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            topic.delete()
            return self.success("删除成功")
        except Topic.DoesNotExist:
            return self.error("专题不存在")


class TopicPracticeAPI(APIView):
    """
    专题练习API
    """
    
    @login_required
    def get(self, request, topic_id):
        """
        开始专题练习 - 获取题目列表
        """
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
            
            # 检查权限
            if not topic.is_public and topic.created_by != request.user and not request.user.is_super_admin:
                return self.error("专题不存在或无权限访问")
            
            # 获取专题题目
            topic_questions = TopicQuestion.objects.filter(
                topic=topic
            ).select_related('question').order_by('order')
            
            questions = []
            for tq in topic_questions:
                question_data = {
                    'id': tq.question.id,
                    'title': tq.question.title,
                    'content': tq.question.content,
                    'options': tq.question.options,
                    'question_type': tq.question.question_type,
                    'difficulty': tq.question.difficulty,
                    'score': tq.question.score,
                    'order': tq.order,
                    'is_required': tq.is_required
                }
                questions.append(question_data)
            
            # 创建练习记录
            practice_record = TopicPracticeRecord.objects.create(
                topic=topic,
                user=request.user,
                status='in_progress',
                total_questions=len(questions),
                start_time=timezone.now()
            )
            
            return self.success({
                'practice_id': practice_record.id,
                'topic': {
                    'id': topic.id,
                    'title': topic.title,
                    'description': topic.description,
                    'difficulty_level': topic.difficulty_level,
                    'estimated_time': topic.estimated_time
                },
                'questions': questions
            })
        except Topic.DoesNotExist:
            return self.error("专题不存在或已禁用")
    
    @login_required
    @validate_serializer(TopicPracticeSubmitSerializer)
    def post(self, request, topic_id):
        """
        提交专题练习答案
        """
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
            answers = request.data.get('answers', {})
            time_spent = request.data.get('time_spent', 0)
            
            # 获取或创建练习记录
            practice_record, created = TopicPracticeRecord.objects.get_or_create(
                topic=topic,
                user=request.user,
                status='in_progress',
                defaults={
                    'start_time': timezone.now(),
                    'total_questions': TopicQuestion.objects.filter(topic=topic).count()
                }
            )
            
            # 获取专题题目
            topic_questions = TopicQuestion.objects.filter(
                topic=topic
            ).select_related('question')
            
            correct_count = 0
            wrong_count = 0
            total_score = 0
            wrong_questions = []
            
            # 判题
            for tq in topic_questions:
                question = tq.question
                question_id = str(question.id)
                user_answer = answers.get(question_id, '')
                
                # 使用判题器判题
                judge = ChoiceQuestionJudge()
                result = judge.judge(question, user_answer)
                
                if result['is_correct']:
                    correct_count += 1
                    total_score += question.score
                else:
                    wrong_count += 1
                    wrong_questions.append({
                        'question_id': question.id,
                        'user_answer': user_answer,
                        'correct_answer': question.correct_answer
                    })
                    
                    # 记录错题
                    TopicWrongQuestionRecord.objects.update_or_create(
                        topic=topic,
                        question=question,
                        user=request.user,
                        defaults={
                            'wrong_answer': user_answer,
                            'correct_answer': question.correct_answer,
                            'is_reviewed': False
                        }
                    )
                    
                    # 同时添加到通用错题本
                    WrongQuestion.add_or_update_wrong_question(
                        user=request.user,
                        question=question,
                        wrong_answer=user_answer,
                        error_type='other'  # 可以根据需要分析错误类型
                    )
            
            # 更新练习记录
            practice_record.status = 'completed'
            practice_record.end_time = timezone.now()
            practice_record.correct_count = correct_count
            practice_record.wrong_count = wrong_count
            practice_record.score = total_score
            practice_record.time_spent = time_spent
            practice_record.answers = answers
            practice_record.save()
            
            return self.success({
                'practice_id': practice_record.id,
                'total_questions': practice_record.total_questions,
                'correct_count': correct_count,
                'wrong_count': wrong_count,
                'score': total_score,
                'time_spent': time_spent,
                'accuracy': round(correct_count / practice_record.total_questions * 100, 2) if practice_record.total_questions > 0 else 0,
                'wrong_questions': wrong_questions
            })
        except Topic.DoesNotExist:
            return self.error("专题不存在或已禁用")


class TopicPracticeRecordAPI(APIView):
    """
    专题练习记录API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户的专题练习记录
        """
        topic_id = request.GET.get('topic_id')
        status_filter = request.GET.get('status')
        
        queryset = TopicPracticeRecord.objects.filter(user=request.user)
        
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        queryset = queryset.select_related('topic').order_by('-start_time')
        
        return self.paginate_data(request, queryset, TopicPracticeRecordSerializer)


class TopicWrongQuestionAPI(APIView):
    """
    专题错题本API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户的专题错题记录
        """
        topic_id = request.GET.get('topic_id')
        is_reviewed = request.GET.get('is_reviewed')
        
        queryset = TopicWrongQuestionRecord.objects.filter(user=request.user)
        
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        if is_reviewed is not None:
            queryset = queryset.filter(is_reviewed=is_reviewed.lower() == 'true')
        
        queryset = queryset.select_related('topic', 'question').order_by('-create_time')
        
        return self.paginate_data(request, queryset, TopicWrongQuestionRecordSerializer)
    
    @login_required
    def put(self, request, record_id):
        """
        标记错题为已复习
        """
        try:
            record = TopicWrongQuestionRecord.objects.get(
                id=record_id,
                user=request.user
            )
            record.is_reviewed = True
            record.review_time = timezone.now()
            record.save()
            
            return self.success("标记成功")
        except TopicWrongQuestionRecord.DoesNotExist:
            return self.error("错题记录不存在")
    
    @login_required
    def delete(self, request, record_id):
        """
        删除错题记录
        """
        try:
            record = TopicWrongQuestionRecord.objects.get(
                id=record_id,
                user=request.user
            )
            record.delete()
            return self.success("删除成功")
        except TopicWrongQuestionRecord.DoesNotExist:
            return self.error("错题记录不存在")


class TopicWrongQuestionStatisticsAPI(APIView):
    """
    专题错题统计API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户的专题错题统计信息
        """
        # 基础统计
        total_wrong = TopicWrongQuestionRecord.objects.filter(user=request.user).count()
        reviewed_count = TopicWrongQuestionRecord.objects.filter(
            user=request.user, is_reviewed=True
        ).count()
        unreviewed_count = total_wrong - reviewed_count
        review_rate = round(reviewed_count / total_wrong * 100, 2) if total_wrong > 0 else 0
        
        # 专题分布统计
        topic_stats = TopicWrongQuestionRecord.objects.filter(
            user=request.user
        ).values(
            'topic__id', 'topic__title'
        ).annotate(
            wrong_count=Count('id')
        ).order_by('-wrong_count')[:10]
        
        topic_distribution = [{
            'topic_id': stat['topic__id'],
            'topic_title': stat['topic__title'],
            'wrong_count': stat['wrong_count']
        } for stat in topic_stats]
        
        # 难度分布统计
        difficulty_stats = TopicWrongQuestionRecord.objects.filter(
            user=request.user
        ).values(
            'question__difficulty'
        ).annotate(
            wrong_count=Count('id')
        ).order_by('question__difficulty')
        
        difficulty_distribution = [{
            'difficulty': stat['question__difficulty'],
            'wrong_count': stat['wrong_count']
        } for stat in difficulty_stats]
        
        data = {
            'total_wrong': total_wrong,
            'reviewed_count': reviewed_count,
            'unreviewed_count': unreviewed_count,
            'review_rate': review_rate,
            'topic_distribution': topic_distribution,
            'difficulty_distribution': difficulty_distribution
        }
        
        return self.success(data)


class TopicStatisticsAPI(APIView):
    """
    专题统计API
    """
    
    @super_admin_required
    def get(self, request, topic_id):
        """
        获取专题统计信息
        """
        try:
            topic = Topic.objects.get(id=topic_id)
            
            # 基础统计
            total_practices = TopicPracticeRecord.objects.filter(topic=topic).count()
            completed_practices = TopicPracticeRecord.objects.filter(
                topic=topic, status='completed'
            ).count()
            
            # 平均分统计
            avg_score = TopicPracticeRecord.objects.filter(
                topic=topic, status='completed'
            ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
            
            # 正确率统计
            practice_records = TopicPracticeRecord.objects.filter(
                topic=topic, status='completed'
            )
            
            total_questions_answered = sum(record.total_questions for record in practice_records)
            total_correct_answers = sum(record.correct_count for record in practice_records)
            overall_accuracy = round(
                total_correct_answers / total_questions_answered * 100, 2
            ) if total_questions_answered > 0 else 0
            
            # 用户参与统计
            unique_users = TopicPracticeRecord.objects.filter(
                topic=topic
            ).values('user').distinct().count()
            
            # 错题统计
            wrong_question_count = TopicWrongQuestionRecord.objects.filter(
                topic=topic
            ).count()
            
            data = {
                'topic_id': topic.id,
                'topic_title': topic.title,
                'total_practices': total_practices,
                'completed_practices': completed_practices,
                'completion_rate': round(completed_practices / total_practices * 100, 2) if total_practices > 0 else 0,
                'avg_score': round(avg_score, 2),
                'overall_accuracy': overall_accuracy,
                'unique_users': unique_users,
                'wrong_question_count': wrong_question_count
            }
            
            return self.success(data)
        except Topic.DoesNotExist:
            return self.error("专题不存在")