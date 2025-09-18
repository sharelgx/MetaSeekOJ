# -*- coding: utf-8 -*-
"""
统一判题API接口
提供编程题和选择题的统一提交和查询接口
"""

import json
import logging
from typing import Dict, Any, List, Optional

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.db import transaction

from account.decorators import login_required
from utils.api import APIView, validate_serializer
from utils.shortcuts import datetime2str, rand_str
from utils.throttling import TokenBucket

from .unified_dispatcher import unified_dispatcher
from .submission_manager import submission_manager
from .serializers import (
    UnifiedSubmissionSerializer,
    SubmissionListSerializer,
    UserStatisticsSerializer
)

logger = logging.getLogger(__name__)


class UnifiedSubmissionAPI(APIView):
    """
    统一提交API
    支持编程题和选择题的统一提交接口
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @login_required
    @validate_serializer(UnifiedSubmissionSerializer)
    def post(self, request):
        """
        统一提交接口
        
        请求参数:
        {
            "question_type": "programming" | "choice",
            "question_id": int,
            "code": str (编程题必需),
            "language": str (编程题必需),
            "selected_answer": str (选择题必需),
            "contest_id": int (可选),
            "captcha": str (可选)
        }
        """
        try:
            data = request.data
            user = request.user
            
            # 提取基本参数
            question_type = data.get('question_type')
            question_id = data.get('question_id')
            contest_id = data.get('contest_id')
            
            # 验证题目类型
            if question_type not in ['programming', 'choice']:
                return self.error("不支持的题目类型")
            
            # 获取客户端信息
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 提交限流检查
            if not self._check_submission_rate_limit(user.id, question_type):
                return self.error("提交过于频繁，请稍后再试")
            
            # 构建提交数据
            submission_data = {
                'user_id': user.id,
                'question_type': question_type,
                'question_id': question_id,
                'contest_id': contest_id,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            
            # 根据题目类型添加特定参数
            if question_type == 'programming':
                submission_data.update({
                    'code': data.get('code', ''),
                    'language': data.get('language', '')
                })
            elif question_type == 'choice':
                submission_data.update({
                    'selected_answer': data.get('selected_answer', '')
                })
            
            # 调用统一判题调度器
            with transaction.atomic():
                result = unified_dispatcher.dispatch_judge(submission_data)
            
            if result['success']:
                return self.success({
                    'submission_id': result['submission_id'],
                    'status': result['status'],
                    'message': result.get('message', '提交成功')
                })
            else:
                return self.error(result.get('error', '提交失败'))
                
        except ValidationError as e:
            logger.warning(f"提交参数验证失败: {e}")
            return self.error(f"参数验证失败: {str(e)}")
        except Exception as e:
            logger.exception(f"统一提交处理失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_submission_rate_limit(self, user_id: int, question_type: str) -> bool:
        """
        检查提交频率限制
        
        Args:
            user_id: 用户ID
            question_type: 题目类型
            
        Returns:
            是否允许提交
        """
        try:
            # 不同题目类型使用不同的限流策略
            if question_type == 'programming':
                # 编程题：每分钟最多5次提交
                bucket_key = f"programming_submission_{user_id}"
                bucket = TokenBucket(bucket_key, capacity=5, refill_rate=5/60)
            else:
                # 选择题：每分钟最多20次提交
                bucket_key = f"choice_submission_{user_id}"
                bucket = TokenBucket(bucket_key, capacity=20, refill_rate=20/60)
            
            return bucket.consume(1)
            
        except Exception as e:
            logger.exception(f"检查提交频率限制失败: {e}")
            # 出错时允许提交，避免影响正常使用
            return True


class UnifiedSubmissionListAPI(APIView):
    """
    统一提交记录列表API
    """
    
    @validate_serializer(SubmissionListSerializer)
    def get(self, request):
        """
        获取提交记录列表
        
        查询参数:
        - user_id: 用户ID (可选)
        - question_id: 题目ID (可选)
        - question_type: 题目类型 (可选: all, programming, choice)
        - result: 结果状态 (可选)
        - page: 页码 (默认: 1)
        - page_size: 每页大小 (默认: 20)
        """
        try:
            data = request.data
            user_id = data.get('user_id')
            question_id = data.get('question_id')
            question_type = data.get('question_type', 'all')
            page = data.get('page', 1)
            page_size = min(data.get('page_size', 20), 100)  # 限制最大页面大小
            
            # 权限检查：普通用户只能查看自己的提交记录
            if not request.user.is_admin_role() and user_id != request.user.id:
                user_id = request.user.id
            
            if user_id:
                # 获取用户提交记录
                result = submission_manager.get_user_submissions(
                    user_id=user_id,
                    question_type=question_type,
                    page=page,
                    page_size=page_size
                )
            elif question_id:
                # 获取题目提交记录
                if question_type == 'all':
                    return self.error("查询题目提交记录时必须指定题目类型")
                
                result = submission_manager.get_question_submissions(
                    question_id=question_id,
                    question_type=question_type,
                    page=page,
                    page_size=page_size
                )
            else:
                # 获取最近提交记录（仅管理员）
                if not request.user.is_admin_role():
                    return self.error("权限不足")
                
                result = submission_manager.get_recent_submissions(
                    limit=page_size,
                    question_type=question_type
                )
            
            if result['success']:
                return self.success(result['data'])
            else:
                return self.error(result.get('error', '查询失败'))
                
        except Exception as e:
            logger.exception(f"获取提交记录列表失败: {e}")
            return self.error("系统错误，请稍后重试")


class UserStatisticsAPI(APIView):
    """
    用户统计信息API
    """
    
    @validate_serializer(UserStatisticsSerializer)
    def get(self, request):
        """
        获取用户统计信息
        
        查询参数:
        - user_id: 用户ID (可选，默认为当前用户)
        """
        try:
            data = request.data
            user_id = data.get('user_id', request.user.id)
            
            # 权限检查：普通用户只能查看自己的统计信息
            if not request.user.is_admin_role() and user_id != request.user.id:
                user_id = request.user.id
            
            result = submission_manager.get_user_statistics(user_id)
            
            if result['success']:
                return self.success(result['data'])
            else:
                return self.error(result.get('error', '获取统计信息失败'))
                
        except Exception as e:
            logger.exception(f"获取用户统计信息失败: {e}")
            return self.error("系统错误，请稍后重试")


class SubmissionDetailAPI(APIView):
    """
    提交详情API
    """
    
    def get(self, request):
        """
        获取提交详情
        
        查询参数:
        - submission_id: 提交ID
        - question_type: 题目类型 (programming 或 choice)
        """
        try:
            submission_id = request.GET.get('submission_id')
            question_type = request.GET.get('question_type')
            
            if not submission_id or not question_type:
                return self.error("缺少必需参数")
            
            if question_type not in ['programming', 'choice']:
                return self.error("不支持的题目类型")
            
            # 根据题目类型获取提交详情
            if question_type == 'programming':
                result = self._get_programming_submission_detail(submission_id, request.user)
            else:
                result = self._get_choice_submission_detail(submission_id, request.user)
            
            if result['success']:
                return self.success(result['data'])
            else:
                return self.error(result.get('error', '获取提交详情失败'))
                
        except Exception as e:
            logger.exception(f"获取提交详情失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    def _get_programming_submission_detail(self, submission_id: int, user) -> Dict[str, Any]:
        """
        获取编程题提交详情
        """
        try:
            from submission.models import Submission
            
            submission = Submission.objects.select_related(
                'problem', 'user'
            ).get(id=submission_id)
            
            # 权限检查
            if not user.is_admin_role() and submission.user_id != user.id:
                return {'success': False, 'error': '权限不足'}
            
            return {
                'success': True,
                'data': {
                    'id': submission.id,
                    'question_type': 'programming',
                    'problem': {
                        'id': submission.problem.id,
                        'title': submission.problem.title,
                        'display_id': submission.problem._id
                    },
                    'user': {
                        'id': submission.user.id,
                        'username': submission.user.username
                    },
                    'code': submission.code,
                    'language': submission.language,
                    'result': submission.result,
                    'info': submission.info,
                    'statistic_info': submission.statistic_info,
                    'create_time': datetime2str(submission.create_time),
                    'contest_id': submission.contest_id,
                    'ip': submission.ip
                }
            }
            
        except Submission.DoesNotExist:
            return {'success': False, 'error': '提交记录不存在'}
        except Exception as e:
            logger.exception(f"获取编程题提交详情失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_choice_submission_detail(self, submission_id: int, user) -> Dict[str, Any]:
        """
        获取选择题提交详情
        """
        try:
            from choice_question.models import ChoiceQuestionSubmission
            
            submission = ChoiceQuestionSubmission.objects.select_related(
                'question', 'user'
            ).get(id=submission_id)
            
            # 权限检查
            if not user.is_admin_role() and submission.user_id != user.id:
                return {'success': False, 'error': '权限不足'}
            
            return {
                'success': True,
                'data': {
                    'id': submission.id,
                    'question_type': 'choice',
                    'question': {
                        'id': submission.question.id,
                        'title': submission.question.title,
                        'display_id': submission.question._id,
                        'question_type': submission.question.question_type,
                        'options': submission.question.options,
                        'correct_answer': submission.question.correct_answer,
                        'explanation': submission.question.explanation
                    },
                    'user': {
                        'id': submission.user.id,
                        'username': submission.user.username
                    },
                    'selected_answer': submission.selected_answer,
                    'is_correct': submission.is_correct,
                    'score': submission.score,
                    'submit_time': datetime2str(submission.submit_time),
                    'time_spent': submission.time_spent,
                    'ip_address': submission.ip_address
                }
            }
            
        except ChoiceQuestionSubmission.DoesNotExist:
            return {'success': False, 'error': '提交记录不存在'}
        except Exception as e:
            logger.exception(f"获取选择题提交详情失败: {e}")
            return {'success': False, 'error': str(e)}


class JudgeStatusAPI(APIView):
    """
    判题状态查询API
    """
    
    def get(self, request):
        """
        查询判题状态
        
        查询参数:
        - submission_id: 提交ID
        - question_type: 题目类型
        """
        try:
            submission_id = request.GET.get('submission_id')
            question_type = request.GET.get('question_type')
            
            if not submission_id or not question_type:
                return self.error("缺少必需参数")
            
            # 获取判题状态
            status = unified_dispatcher.get_judge_status(
                submission_id, question_type
            )
            
            return self.success(status)
            
        except Exception as e:
            logger.exception(f"查询判题状态失败: {e}")
            return self.error("系统错误，请稍后重试")