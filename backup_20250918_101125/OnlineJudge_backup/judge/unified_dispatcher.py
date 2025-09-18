# -*- coding: utf-8 -*-
"""
统一判题调度器
支持编程题和选择题的混合判题
"""

import logging
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone

from problem.models import Problem
from choice_question.models import ChoiceQuestion
from submission.models import Submission
from choice_question.models import ChoiceQuestionSubmission
from .dispatcher import JudgeDispatcher as ProgrammingJudgeDispatcher
from choice_question.utils.judge import ChoiceQuestionJudge

logger = logging.getLogger(__name__)


class QuestionTypeDetector:
    """
    题目类型识别器
    根据题目ID和类型标识判断是编程题还是选择题
    """
    
    @staticmethod
    def detect_question_type(question_id: str, question_type_hint: str = None) -> str:
        """
        检测题目类型
        
        Args:
            question_id: 题目ID
            question_type_hint: 题目类型提示 ('programming' 或 'choice')
            
        Returns:
            'programming' 或 'choice'
        """
        # 如果有明确的类型提示，直接使用
        if question_type_hint in ['programming', 'choice']:
            return question_type_hint
        
        # 尝试从选择题表中查找
        try:
            ChoiceQuestion.objects.get(id=question_id)
            return 'choice'
        except ChoiceQuestion.DoesNotExist:
            pass
        
        # 尝试从编程题表中查找
        try:
            Problem.objects.get(id=question_id)
            return 'programming'
        except Problem.DoesNotExist:
            pass
        
        # 默认返回编程题类型
        logger.warning(f"无法识别题目类型，题目ID: {question_id}，默认为编程题")
        return 'programming'
    
    @staticmethod
    def get_question_object(question_id: str, question_type: str):
        """
        根据题目类型获取题目对象
        
        Args:
            question_id: 题目ID
            question_type: 题目类型
            
        Returns:
            题目对象
        """
        if question_type == 'choice':
            return ChoiceQuestion.objects.get(id=question_id)
        else:
            return Problem.objects.get(id=question_id)


class UnifiedJudgeDispatcher:
    """
    统一判题调度器
    负责协调编程题和选择题的判题流程
    """
    
    def __init__(self):
        self.choice_judge = ChoiceQuestionJudge()
        self._judge_status_cache = {}  # 判题状态缓存
    
    def dispatch_judge(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调度判题任务
        
        Args:
            submission_data: 提交数据，包含:
                - question_id: 题目ID
                - user_id: 用户ID
                - answer: 用户答案（编程题为代码，选择题为选项）
                - question_type: 题目类型提示（可选）
                - language: 编程语言（编程题必需）
                - contest_id: 竞赛ID（可选）
                
        Returns:
            判题结果
        """
        try:
            # 检测题目类型
            question_type = QuestionTypeDetector.detect_question_type(
                submission_data['question_id'],
                submission_data.get('question_type')
            )
            
            # 根据题目类型分发到相应的判题引擎
            if question_type == 'choice':
                return self._judge_choice_question(submission_data)
            else:
                return self._judge_programming_question(submission_data)
                
        except Exception as e:
            logger.exception(f"判题调度失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': {
                    'status': 'System Error',
                    'score': 0,
                    'time_cost': 0,
                    'memory_cost': 0
                }
            }
    
    def _judge_choice_question(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        选择题判题
        
        Args:
            submission_data: 提交数据
            
        Returns:
            判题结果
        """
        try:
            # 获取题目对象
            question = ChoiceQuestion.objects.get(id=submission_data['question_id'])
            
            # 获取用户对象
            from account.models import User
            user = User.objects.get(id=submission_data['user_id'])
            
            # 执行判题
            judge_result = self.choice_judge.judge_submission(
                question=question,
                user_answer=submission_data['answer'],
                user=user,
                save_submission=True
            )
            
            # 更新题目统计
            question.update_statistics(judge_result['is_correct'])
            
            return {
                'success': True,
                'question_type': 'choice',
                'result': {
                    'status': 'Accepted' if judge_result['is_correct'] else 'Wrong Answer',
                    'score': judge_result['score'],
                    'max_score': judge_result['max_score'],
                    'is_correct': judge_result['is_correct'],
                    'user_answer': judge_result['user_answer'],
                    'correct_answer': judge_result['correct_answer'],
                    'explanation': judge_result['explanation'],
                    'time_cost': 0,  # 选择题无时间消耗
                    'memory_cost': 0,  # 选择题无内存消耗
                    'judge_time': judge_result['judge_time'],
                    'details': judge_result['details']
                }
            }
            
        except ChoiceQuestion.DoesNotExist:
            return {
                'success': False,
                'error': '选择题不存在',
                'result': {'status': 'System Error', 'score': 0}
            }
        except Exception as e:
            logger.exception(f"选择题判题失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': {'status': 'System Error', 'score': 0}
            }
    
    def _judge_programming_question(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        编程题判题
        
        Args:
            submission_data: 提交数据
            
        Returns:
            判题结果
        """
        try:
            # 创建提交记录
            from account.models import User
            user = User.objects.get(id=submission_data['user_id'])
            
            submission = Submission.objects.create(
                problem_id=submission_data['question_id'],
                user=user,
                code=submission_data['answer'],
                language=submission_data['language'],
                contest_id=submission_data.get('contest_id')
            )
            
            # 使用原有的编程题判题器
            programming_dispatcher = ProgrammingJudgeDispatcher(
                submission.id, 
                submission_data['question_id']
            )
            
            # 执行判题
            programming_dispatcher.judge()
            
            # 刷新提交记录
            submission.refresh_from_db()
            
            return {
                'success': True,
                'question_type': 'programming',
                'submission_id': submission.id,
                'result': {
                    'status': submission.result,
                    'score': getattr(submission, 'score', 0),
                    'time_cost': submission.statistic_info.get('time_cost', 0) if submission.statistic_info else 0,
                    'memory_cost': submission.statistic_info.get('memory_cost', 0) if submission.statistic_info else 0,
                    'error_info': submission.statistic_info.get('err_info', '') if submission.statistic_info else '',
                    'judge_time': submission.create_time
                }
            }
            
        except Problem.DoesNotExist:
            return {
                'success': False,
                'error': '编程题不存在',
                'result': {'status': 'System Error', 'score': 0}
            }
        except Exception as e:
            logger.exception(f"编程题判题失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': {'status': 'System Error', 'score': 0}
            }


class ResultProcessor:
    """
    统一结果处理器
    负责处理不同类型题目的判题结果
    """
    
    @staticmethod
    def process_result(judge_result: Dict[str, Any], user_id: int, contest_id: Optional[int] = None) -> Dict[str, Any]:
        """
        处理判题结果
        
        Args:
            judge_result: 判题结果
            user_id: 用户ID
            contest_id: 竞赛ID（可选）
            
        Returns:
            处理后的结果
        """
        try:
            # 更新用户统计信息
            ResultProcessor._update_user_statistics(judge_result, user_id)
            
            # 如果是竞赛题目，更新竞赛排名
            if contest_id:
                ResultProcessor._update_contest_ranking(judge_result, user_id, contest_id)
            
            # 记录错题（如果答错）
            if judge_result.get('question_type') == 'choice' and not judge_result['result'].get('is_correct'):
                ResultProcessor._record_wrong_question(judge_result, user_id)
            
            return {
                'success': True,
                'message': '结果处理完成',
                'result': judge_result['result']
            }
            
        except Exception as e:
            logger.exception(f"结果处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': judge_result.get('result', {})
            }
    
    @staticmethod
    def _update_user_statistics(judge_result: Dict[str, Any], user_id: int):
        """
        更新用户统计信息
        """
        # 这里可以添加用户统计信息的更新逻辑
        # 例如：总提交数、正确率、积分等
        pass
    
    @staticmethod
    def _update_contest_ranking(judge_result: Dict[str, Any], user_id: int, contest_id: int):
        """
        更新竞赛排名
        """
        # 这里可以添加竞赛排名的更新逻辑
        pass
    
    @staticmethod
    def _record_wrong_question(judge_result: Dict[str, Any], user_id: int):
        """
        记录错题
        """
        try:
            from choice_question.models import WrongQuestion
            from account.models import User
            
            user = User.objects.get(id=user_id)
            question_id = judge_result['result']['details'].get('question_id')
            
            if question_id:
                question = ChoiceQuestion.objects.get(id=question_id)
                WrongQuestion.objects.get_or_create(
                    user=user,
                    question=question,
                    defaults={
                        'wrong_count': 1,
                        'last_wrong_time': timezone.now()
                    }
                )
        except Exception as e:
            logger.exception(f"记录错题失败: {e}")


    def get_judge_status(self, submission_id: int, question_type: str) -> Dict[str, Any]:
        """
        获取判题状态
        
        Args:
            submission_id: 提交ID
            question_type: 题目类型
            
        Returns:
            判题状态信息
        """
        try:
            if question_type == 'choice':
                return self._get_choice_judge_status(submission_id)
            elif question_type == 'programming':
                return self._get_programming_judge_status(submission_id)
            else:
                return {
                    'success': False,
                    'error': f'不支持的题目类型: {question_type}'
                }
                
        except Exception as e:
            logger.exception(f"获取判题状态失败: {e}")
            return {
                'success': False,
                'error': f'获取判题状态失败: {str(e)}'
            }
    
    def _get_choice_judge_status(self, submission_id: int) -> Dict[str, Any]:
        """
        获取选择题判题状态
        """
        try:
            from choice_question.models import ChoiceQuestionSubmission
            
            submission = ChoiceQuestionSubmission.objects.get(id=submission_id)
            
            return {
                'success': True,
                'status': 'completed',  # 选择题判题是同步的，总是已完成
                'result': 'Accepted' if submission.is_correct else 'Wrong Answer',
                'score': submission.score,
                'submit_time': submission.submit_time.isoformat(),
                'time_spent': submission.time_spent
            }
            
        except ChoiceQuestionSubmission.DoesNotExist:
            return {
                'success': False,
                'error': '提交记录不存在'
            }
    
    def _get_programming_judge_status(self, submission_id: int) -> Dict[str, Any]:
        """
        获取编程题判题状态
        """
        try:
            from submission.models import Submission
            
            submission = Submission.objects.get(id=submission_id)
            
            # 判断判题状态
            if submission.result == -2:  # 判题中
                status = 'judging'
            elif submission.result == -1:  # 等待判题
                status = 'pending'
            else:
                status = 'completed'
            
            return {
                'success': True,
                'status': status,
                'result': submission.result,
                'info': submission.info,
                'statistic_info': submission.statistic_info,
                'create_time': submission.create_time.isoformat()
            }
            
        except Submission.DoesNotExist:
            return {
                'success': False,
                'error': '提交记录不存在'
            }


# 全局调度器实例
unified_dispatcher = UnifiedJudgeDispatcher()