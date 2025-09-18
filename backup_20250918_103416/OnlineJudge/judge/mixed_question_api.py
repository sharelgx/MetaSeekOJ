# -*- coding: utf-8 -*-
"""
混合题目查询API
提供编程题和选择题的统一查询接口
"""

import logging
from typing import Dict, Any, List, Optional
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator

from utils.api import APIView, validate_serializer
from utils.shortcuts import datetime2str
from problem.models import Problem
from choice_question.models import ChoiceQuestion, Category as ChoiceCategory
from .serializers import QuestionMixSerializer

logger = logging.getLogger(__name__)


class MixedQuestionListAPI(APIView):
    """
    混合题目列表API
    支持编程题和选择题的统一查询
    """
    
    @validate_serializer(QuestionMixSerializer)
    def get(self, request):
        """
        获取混合题目列表
        
        查询参数:
        - question_types: 题目类型列表 ['programming', 'choice']
        - difficulty: 难度筛选
        - category_id: 分类ID筛选
        - tag_ids: 标签ID列表筛选
        - keyword: 关键词搜索
        - is_public: 是否只显示公开题目
        - page: 页码
        - page_size: 每页大小
        - order_by: 排序方式
        """
        try:
            data = request.data
            question_types = data.get('question_types', ['programming', 'choice'])
            difficulty = data.get('difficulty')
            category_id = data.get('category_id')
            tag_ids = data.get('tag_ids', [])
            keyword = data.get('keyword')
            is_public = data.get('is_public', True)
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)
            order_by = data.get('order_by', '-create_time')
            
            questions = []
            
            # 获取编程题
            if 'programming' in question_types:
                programming_questions = self._get_programming_questions(
                    difficulty=difficulty,
                    category_id=category_id,
                    tag_ids=tag_ids,
                    keyword=keyword,
                    is_public=is_public
                )
                questions.extend(programming_questions)
            
            # 获取选择题
            if 'choice' in question_types:
                choice_questions = self._get_choice_questions(
                    difficulty=difficulty,
                    category_id=category_id,
                    tag_ids=tag_ids,
                    keyword=keyword,
                    is_public=is_public
                )
                questions.extend(choice_questions)
            
            # 排序
            questions = self._sort_questions(questions, order_by)
            
            # 分页
            paginator = Paginator(questions, page_size)
            page_obj = paginator.get_page(page)
            
            return self.success({
                'questions': list(page_obj),
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            })
            
        except Exception as e:
            logger.exception(f"获取混合题目列表失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    def _get_programming_questions(self, difficulty=None, category_id=None, 
                                 tag_ids=None, keyword=None, is_public=True) -> List[Dict[str, Any]]:
        """
        获取编程题列表
        """
        try:
            queryset = Problem.objects.all()
            
            # 公开性筛选
            if is_public:
                queryset = queryset.filter(visible=True)
            
            # 难度筛选
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            # 标签筛选
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids).distinct()
            
            # 关键词搜索
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) |
                    Q(_id__icontains=keyword)
                )
            
            questions = []
            for problem in queryset.select_related().prefetch_related('tags'):
                questions.append({
                    'id': problem.id,
                    'display_id': problem._id,
                    'title': problem.title,
                    'description': problem.description[:200] + '...' if len(problem.description) > 200 else problem.description,
                    'question_type': 'programming',
                    'difficulty': problem.difficulty,
                    'tags': [{'id': tag.id, 'name': tag.name} for tag in problem.tags.all()],
                    'submission_number': problem.submission_number,
                    'accepted_number': problem.accepted_number,
                    'acceptance_rate': round((problem.accepted_number / problem.submission_number * 100), 2) if problem.submission_number > 0 else 0,
                    'create_time': datetime2str(problem.create_time),
                    'last_update_time': datetime2str(problem.last_update_time),
                    'created_by': {
                        'id': problem.created_by.id,
                        'username': problem.created_by.username
                    } if problem.created_by else None,
                    'is_public': problem.visible,
                    'time_limit': problem.time_limit,
                    'memory_limit': problem.memory_limit,
                    'languages': problem.languages,
                    'template': problem.template,
                    'samples': problem.samples,
                    'hint': problem.hint,
                    'source': problem.source
                })
            
            return questions
            
        except Exception as e:
            logger.exception(f"获取编程题列表失败: {e}")
            return []
    
    def _get_choice_questions(self, difficulty=None, category_id=None, 
                            tag_ids=None, keyword=None, is_public=True) -> List[Dict[str, Any]]:
        """
        获取选择题列表
        """
        try:
            queryset = ChoiceQuestion.objects.all()
            
            # 公开性筛选
            if is_public:
                queryset = queryset.filter(visible=True)
            
            # 难度筛选
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            # 分类筛选
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            # 标签筛选
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids).distinct()
            
            # 关键词搜索
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) |
                    Q(_id__icontains=keyword)
                )
            
            questions = []
            for question in queryset.select_related('category', 'created_by').prefetch_related('tags'):
                questions.append({
                    'id': question.id,
                    'display_id': question._id,
                    'title': question.title,
                    'description': question.description[:200] + '...' if len(question.description) > 200 else question.description,
                    'question_type': 'choice',
                    'choice_type': question.question_type,  # single_choice 或 multiple_choice
                    'difficulty': question.difficulty,
                    'category': {
                        'id': question.category.id,
                        'name': question.category.name
                    } if question.category else None,
                    'tags': [{'id': tag.id, 'name': tag.name} for tag in question.tags.all()],
                    'options': question.options,
                    'score': question.score,
                    'submission_number': question.submission_number,
                    'accepted_number': question.accepted_number,
                    'acceptance_rate': question.acceptance_rate(),
                    'create_time': datetime2str(question.create_time),
                    'last_update_time': datetime2str(question.last_update_time),
                    'created_by': {
                        'id': question.created_by.id,
                        'username': question.created_by.username
                    } if question.created_by else None,
                    'is_public': question.visible,
                    'explanation': question.explanation
                })
            
            return questions
            
        except Exception as e:
            logger.exception(f"获取选择题列表失败: {e}")
            return []
    
    def _sort_questions(self, questions: List[Dict[str, Any]], order_by: str) -> List[Dict[str, Any]]:
        """
        对题目列表进行排序
        """
        try:
            reverse = order_by.startswith('-')
            sort_key = order_by.lstrip('-')
            
            if sort_key == 'create_time':
                questions.sort(key=lambda x: x['create_time'], reverse=reverse)
            elif sort_key == 'difficulty':
                # 难度排序：Easy < Medium < Hard
                difficulty_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
                questions.sort(key=lambda x: difficulty_order.get(x['difficulty'], 0), reverse=reverse)
            elif sort_key == 'submission_number':
                questions.sort(key=lambda x: x['submission_number'], reverse=reverse)
            elif sort_key == 'accepted_number':
                questions.sort(key=lambda x: x['accepted_number'], reverse=reverse)
            elif sort_key == 'acceptance_rate':
                questions.sort(key=lambda x: x['acceptance_rate'], reverse=reverse)
            else:
                # 默认按创建时间排序
                questions.sort(key=lambda x: x['create_time'], reverse=True)
            
            return questions
            
        except Exception as e:
            logger.exception(f"题目排序失败: {e}")
            return questions


class MixedQuestionStatisticsAPI(APIView):
    """
    混合题目统计API
    """
    
    def get(self, request):
        """
        获取混合题目统计信息
        """
        try:
            # 编程题统计
            programming_stats = self._get_programming_statistics()
            
            # 选择题统计
            choice_stats = self._get_choice_statistics()
            
            # 综合统计
            total_questions = programming_stats['total'] + choice_stats['total']
            total_submissions = programming_stats['total_submissions'] + choice_stats['total_submissions']
            
            return self.success({
                'programming': programming_stats,
                'choice': choice_stats,
                'overall': {
                    'total_questions': total_questions,
                    'total_submissions': total_submissions,
                    'programming_ratio': round((programming_stats['total'] / total_questions * 100), 2) if total_questions > 0 else 0,
                    'choice_ratio': round((choice_stats['total'] / total_questions * 100), 2) if total_questions > 0 else 0
                }
            })
            
        except Exception as e:
            logger.exception(f"获取混合题目统计失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    def _get_programming_statistics(self) -> Dict[str, Any]:
        """
        获取编程题统计信息
        """
        try:
            problems = Problem.objects.filter(visible=True)
            total = problems.count()
            
            # 按难度分组统计
            difficulty_stats = problems.values('difficulty').annotate(count=Count('difficulty'))
            difficulty_distribution = {item['difficulty']: item['count'] for item in difficulty_stats}
            
            # 提交统计
            total_submissions = sum(p.submission_number for p in problems)
            total_accepted = sum(p.accepted_number for p in problems)
            
            return {
                'total': total,
                'total_submissions': total_submissions,
                'total_accepted': total_accepted,
                'acceptance_rate': round((total_accepted / total_submissions * 100), 2) if total_submissions > 0 else 0,
                'difficulty_distribution': difficulty_distribution
            }
            
        except Exception as e:
            logger.exception(f"获取编程题统计失败: {e}")
            return {'total': 0, 'total_submissions': 0, 'total_accepted': 0, 'acceptance_rate': 0, 'difficulty_distribution': {}}
    
    def _get_choice_statistics(self) -> Dict[str, Any]:
        """
        获取选择题统计信息
        """
        try:
            questions = ChoiceQuestion.objects.filter(visible=True)
            total = questions.count()
            
            # 按难度分组统计
            difficulty_stats = questions.values('difficulty').annotate(count=Count('difficulty'))
            difficulty_distribution = {item['difficulty']: item['count'] for item in difficulty_stats}
            
            # 按题型分组统计
            type_stats = questions.values('question_type').annotate(count=Count('question_type'))
            type_distribution = {item['question_type']: item['count'] for item in type_stats}
            
            # 提交统计
            total_submissions = sum(q.submission_number for q in questions)
            total_accepted = sum(q.accepted_number for q in questions)
            
            return {
                'total': total,
                'total_submissions': total_submissions,
                'total_accepted': total_accepted,
                'acceptance_rate': round((total_accepted / total_submissions * 100), 2) if total_submissions > 0 else 0,
                'difficulty_distribution': difficulty_distribution,
                'type_distribution': type_distribution
            }
            
        except Exception as e:
            logger.exception(f"获取选择题统计失败: {e}")
            return {'total': 0, 'total_submissions': 0, 'total_accepted': 0, 'acceptance_rate': 0, 'difficulty_distribution': {}, 'type_distribution': {}}