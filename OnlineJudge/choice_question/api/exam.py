# -*- coding: utf-8 -*-
"""
试卷和考试会话API
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.api import APIView as BaseAPIView, CSRFExemptAPIView
import json
import logging
import hashlib
from datetime import timedelta

from ..models import ExamPaper, ExamSession, ChoiceQuestion, WrongQuestion
from ..serializers import ExamPaperSerializer, ExamSessionSerializer

logger = logging.getLogger(__name__)


class ExamReportGenerator:
    """
    考试报告生成器
    """
    
    @staticmethod
    def generate_report(session):
        """
        生成详细的考试报告
        """
        try:
            questions = ChoiceQuestion.objects.filter(
                id__in=session.questions
            )
            
            # 基本信息
            report = {
                'basic_info': {
                    'paper_title': session.paper.title,
                    'student': session.user.username,
                    'start_time': session.start_time.isoformat() if session.start_time else None,
                    'submit_time': session.submit_time.isoformat() if session.submit_time else None,
                    'duration': session.get_actual_duration() if hasattr(session, 'get_actual_duration') else None,
                    'score': getattr(session, 'score', 0),
                    'total_score': session.paper.total_score,
                    'total_questions': len(session.questions)
                },
                'detail_analysis': [],
                'difficulty_analysis': {'easy': 0, 'medium': 0, 'hard': 0},
                'integrity_check': {
                    'tab_switches': getattr(session, 'tab_switches', 0),
                    'copy_attempts': getattr(session, 'copy_attempts', 0),
                    'suspicious_behavior': getattr(session, 'suspicious_behavior', [])
                }
            }
            
            # 题目详细分析
            correct_count = 0
            for q in questions:
                q_id = str(q.id)
                user_answer = session.answers.get(q_id) if session.answers else None
                is_correct = user_answer == getattr(q, 'correct_answer', None)
                
                if is_correct:
                    correct_count += 1
                    report['difficulty_analysis'][q.difficulty] += 1
                
                report['detail_analysis'].append({
                    'question_id': q.id,
                    'question_title': getattr(q, 'title', ''),
                    'difficulty': q.difficulty,
                    'category': getattr(q.category, 'name', None) if hasattr(q, 'category') else None,
                    'user_answer': user_answer,
                    'correct_answer': getattr(q, 'correct_answer', None),
                    'is_correct': is_correct,
                    'explanation': getattr(q, 'explanation', '') if not is_correct else None
                })
            
            report['basic_info']['correct_count'] = correct_count
            report['basic_info']['correct_rate'] = f"{correct_count}/{len(questions)}"
            
            return report
            
        except Exception as e:
            logger.exception(f"生成考试报告失败: {e}")
            return None


class ExamPaperAPI(CSRFExemptAPIView):
    """
    试卷管理API
    """
    
    def get(self, request, paper_id=None):
        """
        获取试卷列表或详情
        """
        try:
            # 处理生成预览请求
            if 'generate-preview' in request.path:
                return self.generate_preview(request)
                
            if paper_id:
                # 获取试卷详情
                try:
                    paper = ExamPaper.objects.get(id=paper_id, is_active=True)
                    serializer = ExamPaperSerializer(paper)
                    return self.success(serializer.data)
                except ExamPaper.DoesNotExist:
                    return self.error("试卷不存在")
            else:
                # 获取试卷列表
                papers = ExamPaper.objects.filter(is_active=True).order_by('-create_time')
                serializer = ExamPaperSerializer(papers, many=True)
                return self.success(serializer.data)
                
        except Exception as e:
            logger.exception(f"获取试卷失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    @transaction.atomic
    def post(self, request, paper_id=None):
        """
        创建试卷或生成预览
        """
        try:
            # 处理生成预览请求
            if 'generate-preview' in request.path:
                return self.generate_preview(request)
                
            data = request.data
            
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
            
            # 验证必需字段
            required_fields = ['title', 'duration', 'question_count']
            for field in required_fields:
                if not data.get(field):
                    return self.error(f"缺少必需字段: {field}")
            
            # 验证数据有效性
            try:
                duration = int(data['duration'])
                question_count = int(data['question_count'])
                total_score = int(data.get('total_score', 100))
                
                if duration <= 0 or question_count <= 0 or total_score <= 0:
                    return self.error("数值必须大于0")
                    
            except (ValueError, TypeError):
                return self.error("数值格式不正确")
            
            # 创建试卷
            paper = ExamPaper.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                duration=duration,
                question_count=question_count,
                total_score=total_score,
                difficulty_distribution=data.get('difficulty_distribution', {}),
                created_by=request.user
            )
            
            # 设置分类和标签
            if data.get('categories'):
                paper.categories.set(data['categories'])
            if data.get('tags'):
                paper.tags.set(data['tags'])
            
            serializer = ExamPaperSerializer(paper)
            return self.success(serializer.data)
            
        except Exception as e:
            logger.exception(f"创建试卷失败: {e}")
            return self.error("创建试卷失败")
    
    def generate_preview(self, request):
        """
        生成试卷预览
        """
        try:
            data = request.data
            
            # 验证必需字段
            required_fields = ['question_count', 'difficulty_distribution']
            for field in required_fields:
                if field not in data:
                    return self.error(f"缺少必需字段: {field}")
            
            question_count = int(data['question_count'])
            difficulty_distribution = data['difficulty_distribution']
            categories = data.get('categories', [])
            tags = data.get('tags', [])
            
            # 构建查询条件
            query = ChoiceQuestion.objects.filter(visible=True)
            
            if categories:
                query = query.filter(category_id__in=categories)
            if tags:
                query = query.filter(tags__in=tags)
            
            # 按难度分配题目
            questions = []
            for difficulty, count in difficulty_distribution.items():
                if count > 0:
                    difficulty_questions = query.filter(difficulty=difficulty).order_by('?')[:count]
                    questions.extend(list(difficulty_questions))
            
            # 如果题目不够，随机补充
            if len(questions) < question_count:
                remaining_count = question_count - len(questions)
                remaining_questions = query.exclude(
                    id__in=[q.id for q in questions]
                ).order_by('?')[:remaining_count]
                questions.extend(list(remaining_questions))
            
            # 序列化题目数据
            from ..serializers import ChoiceQuestionListSerializer
            serializer = ChoiceQuestionListSerializer(questions, many=True)
            
            return self.success({
                'questions': serializer.data,
                'total_count': len(questions),
                'difficulty_distribution': {
                    difficulty: len([q for q in questions if q.difficulty == difficulty])
                    for difficulty in ['easy', 'medium', 'hard']
                }
            })
            
        except Exception as e:
            logger.exception(f"生成试卷预览失败: {e}")
            return self.error("生成预览失败")


class ExamSessionAPI(CSRFExemptAPIView):
    """
    考试会话API
    """
    
    def get(self, request, session_id=None):
        """
        获取考试会话列表或详情
        """
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return self.error("请先登录")
            
        try:
            if session_id:
                # 获取会话详情
                try:
                    session = ExamSession.objects.get(id=session_id, user=request.user)
                    
                    # 检查是否超时
                    if session.status == 'started' and session.is_timeout():
                        session.timeout_exam()
                    
                    serializer = ExamSessionSerializer(session)
                    data = serializer.data
                    
                    # 添加题目详情
                    if session.questions:
                        questions = ChoiceQuestion.objects.filter(id__in=session.questions)
                        question_data = []
                        for i, q in enumerate(questions):
                            question_info = {
                                'id': q.id,
                                'title': getattr(q, 'title', ''),
                                'content': getattr(q, 'content', ''),
                                'description': getattr(q, 'description', ''),
                                'options': q.options,
                                'question_type': q.question_type,
                                'difficulty': q.difficulty,
                                'score': q.score,
                                'order': i + 1  # 添加题目序号
                            }
                            
                            # 获取用户答案
                            user_answer = session.answers.get(str(q.id), [])
                            question_info['user_answer'] = user_answer
                            
                            # 如果考试已结束，显示正确答案和判题结果
                            if session.status in ['submitted', 'timeout']:
                                question_info['correct_answer'] = getattr(q, 'correct_answer', None)
                                question_info['explanation'] = getattr(q, 'explanation', '')
                                question_info['is_correct'] = session.is_answer_correct(q, user_answer)
                            
                            question_data.append(question_info)
                        
                        # 前端期望的字段名是questions，不是question_details
                        data['questions'] = question_data
                        data['question_details'] = question_data  # 保持向后兼容
                        
                        # 添加用户答案映射，供前端ExamReview使用
                        data['user_answers'] = session.answers
                    
                    # 添加剩余时间
                    if hasattr(session, 'get_remaining_time'):
                        data['remaining_time'] = session.get_remaining_time()
                    
                    return self.success(data)
                    
                except ExamSession.DoesNotExist:
                    return self.error("考试会话不存在")
            else:
                # 获取用户的考试会话列表
                sessions = ExamSession.objects.filter(user=request.user).order_by('-create_time')
                
                # 应用筛选条件
                status_filter = request.GET.get('status')
                if status_filter:
                    sessions = sessions.filter(status=status_filter)
                
                start_date = request.GET.get('start_date')
                end_date = request.GET.get('end_date')
                if start_date:
                    sessions = sessions.filter(create_time__date__gte=start_date)
                if end_date:
                    sessions = sessions.filter(create_time__date__lte=end_date)
                
                # 分页处理
                offset = int(request.GET.get('offset', 0))
                limit = int(request.GET.get('limit', 20))
                total = sessions.count()
                
                sessions = sessions[offset:offset + limit]
                serializer = ExamSessionSerializer(sessions, many=True)
                
                return self.success({
                    'results': serializer.data,
                    'total': total
                })
                
        except Exception as e:
            logger.exception(f"获取考试会话失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    @transaction.atomic
    def post(self, request, session_id=None):
        """
        创建考试会话
        """
        try:
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
                
            data = request.data
            
            # 验证必需字段
            paper_id = data.get('paper_id')
            if not paper_id:
                return self.error("缺少试卷ID")
            
            # 获取试卷
            try:
                paper = ExamPaper.objects.get(id=paper_id, is_active=True)
            except ExamPaper.DoesNotExist:
                return self.error("试卷不存在")
            
            # 检查用户是否已有未完成的会话
            existing_session = ExamSession.objects.filter(
                user=request.user,
                paper=paper,
                status__in=['created', 'started']
            ).first()
            
            if existing_session:
                # 返回现有会话而不是报错
                serializer = ExamSessionSerializer(existing_session)
                return self.success(serializer.data)
            
            # 生成题目
            questions = self._generate_questions_for_paper(paper)
            if not questions:
                return self.error("无法生成足够的题目")
            
            # 创建考试会话
            session = ExamSession.objects.create(
                user=request.user,
                paper=paper,
                questions=[q.id for q in questions],
                total_count=len(questions),
                status='created'
            )
            
            serializer = ExamSessionSerializer(session)
            return self.success(serializer.data)
            
        except Exception as e:
            logger.exception(f"创建考试会话失败: {e}")
            return self.error("创建考试会话失败")
    
    def _generate_questions_for_paper(self, paper):
        """
        为试卷生成题目
        """
        try:
            # 构建查询条件
            query = ChoiceQuestion.objects.filter(visible=True)
            
            # 按分类筛选（包含子分类）
            if hasattr(paper, 'categories') and paper.categories.exists():
                # 获取所有分类及其子分类的ID
                category_ids = []
                for category in paper.categories.all():
                    category_ids.append(category.id)
                    
                    # 递归获取子分类
                    def get_child_categories(parent):
                        from ..models import Category
                        children = Category.objects.filter(parent=parent)
                        for child in children:
                            category_ids.append(child.id)
                            get_child_categories(child)
                    
                    get_child_categories(category)
                
                query = query.filter(category_id__in=category_ids)
            
            # 按标签筛选
            if hasattr(paper, 'tags') and paper.tags.exists():
                query = query.filter(tags__in=paper.tags.all())
            
            # 按难度分配题目
            questions = []
            difficulty_distribution = getattr(paper, 'difficulty_distribution', {}) or {}
            
            for difficulty, count in difficulty_distribution.items():
                if count > 0:
                    difficulty_questions = query.filter(difficulty=difficulty).order_by('?')[:count]
                    questions.extend(list(difficulty_questions))
            
            # 如果题目不够，随机补充
            target_count = getattr(paper, 'question_count', 10)
            if len(questions) < target_count:
                remaining_count = target_count - len(questions)
                remaining_questions = query.exclude(
                    id__in=[q.id for q in questions]
                ).order_by('?')[:remaining_count]
                questions.extend(list(remaining_questions))
            
            return questions[:target_count]
            
        except Exception as e:
            logger.exception(f"生成题目失败: {e}")
            return []


class ExamSessionActionAPI(CSRFExemptAPIView):
    """
    考试会话操作API
    """
    
    def post(self, request, session_id=None):
        """
        考试会话操作（开始、提交答案、提交考试、防作弊记录、自动保存等）
        """
        try:
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
                
            # 从URL路径中获取session_id，如果没有则从请求数据中获取
            if not session_id:
                session_id = request.data.get('session_id')
            
            if not session_id:
                return self.error("缺少会话ID")
            
            # 防止重复提交
            if not self._prevent_duplicate_submission(session_id, request.user.id, request.path):
                return self.error("请勿重复提交")
            
            # 根据URL路径确定操作类型
            if 'start' in request.path:
                return self._start_session(request, session_id)
            elif 'answer' in request.path:
                return self._submit_answer(request, session_id)
            elif 'submit' in request.path:
                return self._submit_exam(request, session_id)
            elif 'auto-save' in request.path:
                return self._auto_save(request, session_id)
            elif 'record-behavior' in request.path:
                return self._record_behavior(request, session_id)
            elif 'generate-report' in request.path:
                return self._generate_report(request, session_id)
            else:
                return self.error("未知的操作类型")
                
        except Exception as e:
            logger.exception(f"考试会话操作失败: {e}")
            return self.error("操作失败")
    
    def _prevent_duplicate_submission(self, session_id, user_id, path):
        """
        防止重复提交
        """
        try:
            key = hashlib.md5(f"{session_id}_{user_id}_{path}".encode()).hexdigest()
            
            if cache.get(key):
                return False  # 已提交
            
            cache.set(key, True, 5)  # 5秒内不能重复提交
            return True
        except Exception:
            return True  # 缓存失败时允许提交
    
    @transaction.atomic
    def _start_session(self, request, session_id):
        """
        开始考试
        """
        try:
            session = ExamSession.objects.select_for_update().get(
                id=session_id, 
                user=request.user
            )
            
            if session.status != 'created':
                return self.error("考试会话状态不正确")
            
            # 开始考试
            if hasattr(session, 'start_exam'):
                session.start_exam()
            else:
                session.status = 'started'
                session.start_time = timezone.now()
                session.save()
            
            serializer = ExamSessionSerializer(session)
            return self.success(serializer.data)
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
        except Exception as e:
            logger.exception(f"开始考试失败: {e}")
            return self.error("开始考试失败，请稍后重试")
    
    @transaction.atomic
    def _auto_save(self, request, session_id):
        """
        自动保存考试进度
        """
        try:
            session = ExamSession.objects.select_for_update().get(
                id=session_id, 
                user=request.user
            )
            
            if session.status != 'started':
                return self.error("考试未开始或已结束")
            
            # 检查是否超时
            if hasattr(session, 'is_timeout') and session.is_timeout():
                if hasattr(session, 'timeout_exam'):
                    session.timeout_exam()
                else:
                    session.status = 'timeout'
                    session.save()
                return self.error("考试已超时")
            
            answers = request.data.get('answers', {})
            
            if answers:
                # 批量更新答案
                if not hasattr(session, 'answers') or session.answers is None:
                    session.answers = {}
                session.answers.update(answers)
                session.save()
            
            return self.success({
                'saved': True,
                'timestamp': timezone.now().isoformat(),
                'saved_count': len(answers)
            })
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
        except Exception as e:
            logger.exception(f"自动保存失败: {e}")
            return self.error("自动保存失败，请稍后重试")
    
    @transaction.atomic
    def _record_behavior(self, request, session_id):
        """
        记录防作弊行为
        """
        try:
            session = ExamSession.objects.select_for_update().get(
                id=session_id, 
                user=request.user
            )
            
            if session.status != 'started':
                return self.error("考试未开始或已结束")
            
            behavior_type = request.data.get('type')
            behavior_data = request.data.get('data', {})
            
            if not behavior_type:
                return self.error("缺少行为类型")
            
            # 初始化防作弊字段（如果不存在）
            if not hasattr(session, 'tab_switches'):
                session.tab_switches = 0
            if not hasattr(session, 'copy_attempts'):
                session.copy_attempts = 0
            if not hasattr(session, 'suspicious_behavior'):
                session.suspicious_behavior = []
            
            # 记录不同类型的行为
            if behavior_type == 'tab_switch':
                session.tab_switches = getattr(session, 'tab_switches', 0) + 1
                session.suspicious_behavior.append({
                    'type': 'tab_switch',
                    'time': timezone.now().isoformat(),
                    'count': session.tab_switches,
                    'data': behavior_data
                })
            elif behavior_type == 'copy_attempt':
                session.copy_attempts = getattr(session, 'copy_attempts', 0) + 1
                session.suspicious_behavior.append({
                    'type': 'copy_attempt',
                    'time': timezone.now().isoformat(),
                    'count': session.copy_attempts,
                    'data': behavior_data
                })
            elif behavior_type == 'right_click':
                session.suspicious_behavior.append({
                    'type': 'right_click',
                    'time': timezone.now().isoformat(),
                    'data': behavior_data
                })
            elif behavior_type == 'key_combination':
                session.suspicious_behavior.append({
                    'type': 'key_combination',
                    'time': timezone.now().isoformat(),
                    'keys': behavior_data.get('keys', []),
                    'data': behavior_data
                })
            
            session.save()
            
            # 检查是否需要警告
            warning = None
            if getattr(session, 'tab_switches', 0) > 5:
                warning = "频繁切换标签页可能影响考试成绩"
            elif getattr(session, 'copy_attempts', 0) > 3:
                warning = "多次尝试复制内容可能影响考试成绩"
            
            return self.success({
                'recorded': True,
                'warning': warning,
                'tab_switches': getattr(session, 'tab_switches', 0),
                'copy_attempts': getattr(session, 'copy_attempts', 0)
            })
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
    
    def _generate_report(self, request, session_id):
        """
        生成考试报告
        """
        try:
            session = ExamSession.objects.get(
                id=session_id, 
                user=request.user
            )
            
            if session.status not in ['submitted', 'timeout']:
                return self.error("考试尚未结束")
            
            # 生成报告
            report = ExamReportGenerator.generate_report(session)
            
            if not report:
                return self.error("生成报告失败")
            
            return self.success(report)
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
    
    @transaction.atomic
    def _submit_answer(self, request, session_id):
        """
        提交答案
        """
        try:
            session = ExamSession.objects.select_for_update().get(
                id=session_id, 
                user=request.user
            )
            
            if session.status != 'started':
                return self.error("考试未开始或已结束")
            
            # 检查是否超时
            if hasattr(session, 'is_timeout') and session.is_timeout():
                if hasattr(session, 'timeout_exam'):
                    session.timeout_exam()
                else:
                    session.status = 'timeout'
                    session.save()
                return self.error("考试已超时")
            
            question_id = request.data.get('question_id')
            answer = request.data.get('answer')
            
            if not question_id or answer is None:
                return self.error("缺少题目ID或答案")
            
            # 验证题目是否属于当前会话
            if str(question_id) not in [str(qid) for qid in session.questions]:
                return self.error("题目不属于当前考试")
            
            # 提交答案
            if hasattr(session, 'submit_answer'):
                session.submit_answer(question_id, answer)
            else:
                # 兼容处理
                if not hasattr(session, 'answers') or session.answers is None:
                    session.answers = {}
                session.answers[str(question_id)] = answer
                session.save()
            
            return self.success({"message": "答案提交成功"})
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
        except ValueError as e:
            logger.error(f"答案提交参数错误: {e}")
            return self.error("参数格式错误")
        except Exception as e:
            logger.exception(f"提交答案失败: {e}")
            return self.error("提交答案失败，请稍后重试")
    
    @transaction.atomic
    def _submit_exam(self, request, session_id):
        """
        提交考试
        """
        try:
            session = ExamSession.objects.select_for_update().get(
                id=session_id, 
                user=request.user
            )
            
            if session.status not in ['started', 'timeout']:
                return self.error("考试状态不正确")
            
            # 提交考试前先记录错题
            self._record_wrong_questions(session)
            
            # 提交考试
            if hasattr(session, 'submit_exam'):
                session.submit_exam()
            else:
                # 兼容处理
                session.status = 'submitted'
                session.submit_time = timezone.now()
                # 计算成绩
                if hasattr(session, 'calculate_score'):
                    session.calculate_score()
                session.save()
            
            serializer = ExamSessionSerializer(session)
            return self.success(serializer.data)
            
        except ExamSession.DoesNotExist:
            return self.error("考试会话不存在")
        except Exception as e:
            logger.exception(f"提交考试失败: {e}")
            return self.error("提交考试失败，请稍后重试")
    
    def _record_wrong_questions(self, session):
        """
        记录错题到错题本
        """
        try:
            if not session.questions or not session.answers:
                return
            
            # 获取所有题目
            questions = ChoiceQuestion.objects.filter(id__in=session.questions)
            
            for question in questions:
                question_id = str(question.id)
                user_answer = session.answers.get(question_id)
                
                # 检查答案是否正确
                if user_answer and not session.is_answer_correct(question, user_answer):
                    # 记录错题
                    WrongQuestion.add_or_update_wrong_question(
                        user=session.user,
                        question=question,
                        wrong_answer=user_answer,
                        error_type='other'  # 默认错误类型，用户可以后续修改
                    )
                    
        except Exception as e:
            logger.exception(f"记录错题失败: {e}")
            # 不影响考试提交，只记录日志


# API设计已统一为类视图，移除了兼容性函数视图