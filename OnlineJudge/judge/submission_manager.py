# -*- coding: utf-8 -*-
"""
统一提交管理器
管理编程题和选择题的提交记录
"""

import logging
from typing import List, Dict, Any, Optional, Union
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator

from account.models import User
from problem.models import Problem
from submission.models import Submission
from choice_question.models import ChoiceQuestion, ChoiceQuestionSubmission

logger = logging.getLogger(__name__)


class SubmissionManager:
    """
    统一提交管理器
    提供编程题和选择题提交记录的统一管理接口
    """
    
    def get_user_submissions(self, user_id: int, question_type: str = 'all', 
                           page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        获取用户的提交记录
        
        Args:
            user_id: 用户ID
            question_type: 题目类型 ('all', 'programming', 'choice')
            page: 页码
            page_size: 每页大小
            
        Returns:
            提交记录列表和分页信息
        """
        try:
            submissions = []
            
            # 获取编程题提交记录
            if question_type in ['all', 'programming']:
                programming_submissions = Submission.objects.filter(
                    user_id=user_id
                ).select_related('problem', 'user').order_by('-create_time')
                
                for sub in programming_submissions:
                    submissions.append({
                        'id': sub.id,
                        'question_type': 'programming',
                        'question_id': sub.problem.id,
                        'question_title': sub.problem.title,
                        'question_display_id': sub.problem._id,
                        'result': sub.result,
                        'score': getattr(sub, 'score', 0),
                        'language': sub.language,
                        'submit_time': sub.create_time,
                        'time_cost': sub.statistic_info.get('time_cost', 0) if sub.statistic_info else 0,
                        'memory_cost': sub.statistic_info.get('memory_cost', 0) if sub.statistic_info else 0,
                        'code_length': len(sub.code) if sub.code else 0,
                        'contest_id': sub.contest_id,
                        'ip_address': sub.ip,
                        'user_agent': getattr(sub, 'user_agent', '')
                    })
            
            # 获取选择题提交记录
            if question_type in ['all', 'choice']:
                choice_submissions = ChoiceQuestionSubmission.objects.filter(
                    user_id=user_id
                ).select_related('question', 'user').order_by('-submit_time')
                
                for sub in choice_submissions:
                    submissions.append({
                        'id': sub.id,
                        'question_type': 'choice',
                        'question_id': sub.question.id,
                        'question_title': sub.question.title,
                        'question_display_id': sub.question._id,
                        'result': 'Accepted' if sub.is_correct else 'Wrong Answer',
                        'score': sub.score,
                        'selected_answer': sub.selected_answer,
                        'correct_answer': sub.question.correct_answer,
                        'submit_time': sub.submit_time,
                        'time_spent': sub.time_spent,
                        'difficulty': sub.question.difficulty,
                        'category': sub.question.category.name if sub.question.category else None,
                        'ip_address': sub.ip_address,
                        'user_agent': sub.user_agent
                    })
            
            # 按提交时间排序
            submissions.sort(key=lambda x: x['submit_time'], reverse=True)
            
            # 分页处理
            paginator = Paginator(submissions, page_size)
            page_obj = paginator.get_page(page)
            
            return {
                'success': True,
                'data': {
                    'submissions': list(page_obj),
                    'total': paginator.count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
        except Exception as e:
            logger.exception(f"获取用户提交记录失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {'submissions': [], 'total': 0}
            }
    
    def get_question_submissions(self, question_id: int, question_type: str, 
                               page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        获取题目的提交记录
        
        Args:
            question_id: 题目ID
            question_type: 题目类型 ('programming' 或 'choice')
            page: 页码
            page_size: 每页大小
            
        Returns:
            提交记录列表和分页信息
        """
        try:
            if question_type == 'programming':
                submissions = Submission.objects.filter(
                    problem_id=question_id
                ).select_related('user').order_by('-create_time')
                
                # 分页处理
                paginator = Paginator(submissions, page_size)
                page_obj = paginator.get_page(page)
                
                submission_list = []
                for sub in page_obj:
                    submission_list.append({
                        'id': sub.id,
                        'user_id': sub.user.id,
                        'username': sub.user.username,
                        'result': sub.result,
                        'score': getattr(sub, 'score', 0),
                        'language': sub.language,
                        'submit_time': sub.create_time,
                        'time_cost': sub.statistic_info.get('time_cost', 0) if sub.statistic_info else 0,
                        'memory_cost': sub.statistic_info.get('memory_cost', 0) if sub.statistic_info else 0,
                        'code_length': len(sub.code) if sub.code else 0
                    })
                    
            elif question_type == 'choice':
                submissions = ChoiceQuestionSubmission.objects.filter(
                    question_id=question_id
                ).select_related('user').order_by('-submit_time')
                
                # 分页处理
                paginator = Paginator(submissions, page_size)
                page_obj = paginator.get_page(page)
                
                submission_list = []
                for sub in page_obj:
                    submission_list.append({
                        'id': sub.id,
                        'user_id': sub.user.id,
                        'username': sub.user.username,
                        'result': 'Accepted' if sub.is_correct else 'Wrong Answer',
                        'score': sub.score,
                        'selected_answer': sub.selected_answer,
                        'submit_time': sub.submit_time,
                        'time_spent': sub.time_spent
                    })
            else:
                return {
                    'success': False,
                    'error': '不支持的题目类型',
                    'data': {'submissions': [], 'total': 0}
                }
            
            return {
                'success': True,
                'data': {
                    'submissions': submission_list,
                    'total': paginator.count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
        except Exception as e:
            logger.exception(f"获取题目提交记录失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {'submissions': [], 'total': 0}
            }
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户的统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户统计信息
        """
        try:
            # 编程题统计
            programming_stats = self._get_programming_statistics(user_id)
            
            # 选择题统计
            choice_stats = self._get_choice_statistics(user_id)
            
            # 综合统计
            total_submissions = programming_stats['total_submissions'] + choice_stats['total_submissions']
            total_accepted = programming_stats['accepted_submissions'] + choice_stats['accepted_submissions']
            
            return {
                'success': True,
                'data': {
                    'programming': programming_stats,
                    'choice': choice_stats,
                    'overall': {
                        'total_submissions': total_submissions,
                        'accepted_submissions': total_accepted,
                        'acceptance_rate': round((total_accepted / total_submissions * 100), 2) if total_submissions > 0 else 0,
                        'total_score': programming_stats['total_score'] + choice_stats['total_score']
                    }
                }
            }
            
        except Exception as e:
            logger.exception(f"获取用户统计信息失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _get_programming_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取编程题统计信息
        """
        submissions = Submission.objects.filter(user_id=user_id)
        total_submissions = submissions.count()
        accepted_submissions = submissions.filter(result='Accepted').count()
        
        # 按结果分组统计
        result_stats = submissions.values('result').annotate(count=Count('result'))
        result_distribution = {item['result']: item['count'] for item in result_stats}
        
        # 按语言分组统计
        language_stats = submissions.values('language').annotate(count=Count('language'))
        language_distribution = {item['language']: item['count'] for item in language_stats}
        
        return {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': round((accepted_submissions / total_submissions * 100), 2) if total_submissions > 0 else 0,
            'total_score': sum([getattr(sub, 'score', 0) for sub in submissions]),
            'result_distribution': result_distribution,
            'language_distribution': language_distribution
        }
    
    def _get_choice_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取选择题统计信息
        """
        submissions = ChoiceQuestionSubmission.objects.filter(user_id=user_id)
        total_submissions = submissions.count()
        accepted_submissions = submissions.filter(is_correct=True).count()
        
        # 按难度分组统计
        difficulty_stats = submissions.values('question__difficulty').annotate(count=Count('question__difficulty'))
        difficulty_distribution = {item['question__difficulty']: item['count'] for item in difficulty_stats}
        
        # 按分类分组统计
        category_stats = submissions.values('question__category__name').annotate(count=Count('question__category__name'))
        category_distribution = {item['question__category__name']: item['count'] for item in category_stats if item['question__category__name']}
        
        return {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': round((accepted_submissions / total_submissions * 100), 2) if total_submissions > 0 else 0,
            'total_score': sum([sub.score for sub in submissions]),
            'average_score': submissions.aggregate(avg_score=Avg('score'))['avg_score'] or 0,
            'difficulty_distribution': difficulty_distribution,
            'category_distribution': category_distribution
        }
    
    def get_recent_submissions(self, limit: int = 10, question_type: str = 'all') -> Dict[str, Any]:
        """
        获取最近的提交记录
        
        Args:
            limit: 限制数量
            question_type: 题目类型 ('all', 'programming', 'choice')
            
        Returns:
            最近提交记录列表
        """
        try:
            submissions = []
            
            # 获取编程题最近提交
            if question_type in ['all', 'programming']:
                programming_submissions = Submission.objects.select_related(
                    'problem', 'user'
                ).order_by('-create_time')[:limit]
                
                for sub in programming_submissions:
                    submissions.append({
                        'id': sub.id,
                        'question_type': 'programming',
                        'question_title': sub.problem.title,
                        'question_display_id': sub.problem._id,
                        'username': sub.user.username,
                        'result': sub.result,
                        'language': sub.language,
                        'submit_time': sub.create_time
                    })
            
            # 获取选择题最近提交
            if question_type in ['all', 'choice']:
                choice_submissions = ChoiceQuestionSubmission.objects.select_related(
                    'question', 'user'
                ).order_by('-submit_time')[:limit]
                
                for sub in choice_submissions:
                    submissions.append({
                        'id': sub.id,
                        'question_type': 'choice',
                        'question_title': sub.question.title,
                        'question_display_id': sub.question._id,
                        'username': sub.user.username,
                        'result': 'Accepted' if sub.is_correct else 'Wrong Answer',
                        'submit_time': sub.submit_time
                    })
            
            # 按提交时间排序并限制数量
            submissions.sort(key=lambda x: x['submit_time'], reverse=True)
            submissions = submissions[:limit]
            
            return {
                'success': True,
                'data': {'submissions': submissions}
            }
            
        except Exception as e:
            logger.exception(f"获取最近提交记录失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {'submissions': []}
            }


# 全局提交管理器实例
submission_manager = SubmissionManager()