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
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.api import APIView as BaseAPIView, CSRFExemptAPIView
import json
import logging
import hashlib
from datetime import timedelta
from typing import Dict, Any

from ..models import ExamPaper, ExamSession, ChoiceQuestion, WrongQuestion, Category
from django.db import models
from ..serializers import ExamPaperSerializer, ExamSessionSerializer
from ..utils.importer import QuestionImporter

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
                queryset = ExamPaper.objects.filter(is_active=True)
                
                # 分类筛选
                category_id = request.GET.get('category')
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                        # 包含子分类的试卷
                        categories = category.get_descendants(include_self=True)
                        queryset = queryset.filter(categories__in=categories).distinct()
                    except Category.DoesNotExist:
                        pass
                
                # 试卷类型筛选
                paper_type = request.GET.get('paper_type')
                if paper_type and paper_type in ['dynamic', 'fixed']:
                    queryset = queryset.filter(paper_type=paper_type)
                
                # 关键词搜索
                keyword = request.GET.get('keyword', '').strip()
                if keyword:
                    queryset = queryset.filter(
                        Q(title__icontains=keyword) |
                        Q(description__icontains=keyword)
                    )
                
                # 排序
                order_by = request.GET.get('order_by', 'create_time')
                order_direction = request.GET.get('order_direction', 'desc')
                
                if order_by == 'import_order':
                    # 按导入顺序排序（仅对固定题目试卷有效）
                    if order_direction == 'asc':
                        queryset = queryset.order_by('create_time')
                    else:
                        queryset = queryset.order_by('-create_time')
                elif order_by == 'title':
                    if order_direction == 'asc':
                        queryset = queryset.order_by('title')
                    else:
                        queryset = queryset.order_by('-title')
                elif order_by == 'question_count':
                    if order_direction == 'asc':
                        queryset = queryset.order_by('question_count')
                    else:
                        queryset = queryset.order_by('-question_count')
                else:  # 默认按创建时间排序
                    if order_direction == 'asc':
                        queryset = queryset.order_by('create_time')
                    else:
                        queryset = queryset.order_by('-create_time')
                
                # 分页处理
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 20))
                
                paginator = Paginator(queryset, page_size)
                try:
                    page_obj = paginator.page(page)
                except:
                    page_obj = paginator.page(1)
                
                serializer = ExamPaperSerializer(page_obj.object_list, many=True)
                return self.success({
                    'results': serializer.data,
                    'total': paginator.count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages
                })
                
        except Exception as e:
            logger.exception(f"获取试卷失败: {e}")
            return self.error("系统错误，请稍后重试")
    
    @transaction.atomic
    def post(self, request, paper_id=None):
        """
        创建试卷、生成预览或批量删除
        """
        try:
            # 处理生成预览请求
            if 'generate-preview' in request.path:
                return self.generate_preview(request)
                
            # 处理批量删除请求
            if 'batch-delete' in request.path:
                return self.delete(request, paper_id)
                
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
    
    @transaction.atomic
    def put(self, request, paper_id=None):
        """
        更新试卷信息
        """
        try:
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
            
            if not paper_id:
                return self.error("缺少试卷ID")
            
            # 获取试卷
            try:
                paper = ExamPaper.objects.get(id=paper_id, is_active=True)
            except ExamPaper.DoesNotExist:
                return self.error("试卷不存在")
            
            data = request.data
            
            # 验证必需字段
            if 'title' in data and not data['title']:
                return self.error("试卷标题不能为空")
            
            # 验证数值字段
            numeric_fields = ['duration', 'question_count', 'total_score']
            for field in numeric_fields:
                if field in data:
                    try:
                        value = int(data[field])
                        if value <= 0:
                            return self.error(f"{field}必须大于0")
                    except (ValueError, TypeError):
                        return self.error(f"{field}格式不正确")
            
            # 更新基本字段
            updatable_fields = ['title', 'description', 'duration', 'question_count', 'total_score', 'difficulty_distribution']
            for field in updatable_fields:
                if field in data:
                    setattr(paper, field, data[field])
            
            # 更新分类和标签
            if 'categories' in data:
                paper.categories.set(data['categories'])
            if 'tags' in data:
                paper.tags.set(data['tags'])
            
            # 更新时间戳
            paper.last_update_time = timezone.now()
            paper.save()
            
            serializer = ExamPaperSerializer(paper)
            return self.success(serializer.data)
            
        except Exception as e:
            logger.exception(f"更新试卷失败: {e}")
            return self.error("更新试卷失败")
    
    @transaction.atomic
    def delete(self, request, paper_id=None):
        """
        批量删除试卷
        """
        try:
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
            
            # 获取要删除的试卷ID列表
            if paper_id:
                # 单个删除
                paper_ids = [paper_id]
            else:
                # 批量删除
                data = request.data
                paper_ids = data.get('ids', [])
                
                if not paper_ids:
                    return self.error("请选择要删除的试卷")
                
                if not isinstance(paper_ids, list):
                    return self.error("参数格式错误")
            
            # 验证试卷存在性和权限
            papers = ExamPaper.objects.filter(
                id__in=paper_ids,
                is_active=True
            )
            
            if not papers.exists():
                return self.error("未找到要删除的试卷")
            
            found_ids = list(papers.values_list('id', flat=True))
            missing_ids = [pid for pid in paper_ids if pid not in found_ids]
            
            if missing_ids:
                return self.error(f"试卷不存在或已删除: {missing_ids}")
            
            # 检查是否有正在进行的考试
            active_sessions = ExamSession.objects.filter(
                paper__in=papers,
                status__in=['not_started', 'in_progress']
            )
            
            if active_sessions.exists():
                return self.error("存在正在进行的考试，无法删除试卷")
            
            # 执行软删除（只标记为非活跃状态，不删除试题数据）
            deleted_count = papers.update(
                is_active=False,
                last_update_time=timezone.now()
            )
            
            # 记录删除操作日志
            logger.info(f"用户 {request.user.username} 批量删除了 {deleted_count} 份试卷: {paper_ids}")
            
            return self.success({
                'message': f'成功删除 {deleted_count} 份试卷',
                'deleted_count': deleted_count,
                'deleted_ids': found_ids
            })
            
        except Exception as e:
            logger.exception(f"批量删除试卷失败: {e}")
            return self.error("删除试卷失败，请稍后重试")
    
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


class ExamPaperImportAPI(CSRFExemptAPIView):
    """
    试卷导入API
    """
    
    @transaction.atomic
    def post(self, request):
        """
        从JSON数据或文件导入整套试卷
        """
        try:
            # 验证用户权限
            if not request.user.is_authenticated:
                return self.error("请先登录")
            
            # 支持两种导入方式：文件上传和直接JSON数据
            if 'file' in request.FILES:
                # 文件上传方式
                uploaded_file = request.FILES['file']
                
                # 验证文件类型
                if not uploaded_file.name.endswith('.json'):
                    return self.error("只支持JSON格式文件")
                
                # 获取其他参数
                category_name = request.data.get('category_name')
                paper_title = request.data.get('paper_title')
                language = request.data.get('language')
                use_import_order = request.data.get('use_import_order', True)
                
                # 保存临时文件
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False) as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                try:
                    # 使用QuestionImporter导入试卷
                    importer = QuestionImporter(user=request.user)
                    result = importer.import_paper_from_json(
                        file_path=temp_file_path,
                        category_name=category_name,
                        paper_title=paper_title,
                        language=language,
                        use_import_order=use_import_order
                    )
                    
                    return self.success({
                        'message': '试卷导入成功',
                        'paper_id': result['paper_id'],
                        'paper_title': result['paper_title'],
                        'imported_questions': result['success_count'],
                        'logs': result['logs']
                    })
                    
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            
            else:
                # 直接JSON数据方式（前端发送的格式）
                data = request.data
                
                # 获取参数
                paper_title = data.get('title')
                description = data.get('description', '')
                questions_data = data.get('questions', [])
                category_id = data.get('category_id')
                language = data.get('language', 'zh-CN')
                use_import_order = data.get('use_import_order', False)
                duration = data.get('duration', 60)
                total_score = data.get('total_score')
                
                if not paper_title:
                    return self.error("试卷标题不能为空")
                
                if not questions_data:
                    return self.error("题目数据不能为空")
                
                # 检查是否选择了现有试卷
                existing_paper = None
                try:
                    existing_paper = ExamPaper.objects.get(
                        title=paper_title,
                        created_by=request.user,
                        is_active=True
                    )
                except ExamPaper.DoesNotExist:
                    pass
                
                # 获取分类
                category = None
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                    except Category.DoesNotExist:
                        return self.error("指定的分类不存在")
                
                # 批量导入题目
                imported_questions = []
                importer = QuestionImporter(user=request.user)
                
                for i, question_data in enumerate(questions_data):
                    # 转换前端数据格式为后端期望格式
                    converted_data = self._convert_frontend_question_format(question_data)
                    # 不要在单个题目数据中添加import_order和language，这些是试卷级别的字段
                    if category:
                        converted_data['category'] = category.name
                    
                    question = importer._import_single_question_for_paper(converted_data)
                    imported_questions.append(question)
                
                from ..models import ExamPaperQuestion
                
                if existing_paper:
                    # 向现有试卷添加题目
                    paper = existing_paper
                    
                    # 获取当前试卷中题目的最大序号
                    max_order = ExamPaperQuestion.objects.filter(paper=paper).aggregate(
                        max_order=models.Max('order')
                    )['max_order'] or 0
                    
                    # 添加新题目到现有试卷
                    for i, question in enumerate(imported_questions):
                        ExamPaperQuestion.objects.create(
                            paper=paper,
                            question=question,
                            order=max_order + i + 1,
                            score=question.score
                        )
                    
                    # 更新试卷统计信息
                    paper.question_count += len(imported_questions)
                    paper.total_score += sum(q.score for q in imported_questions)
                    paper.save()
                    
                    # 关联分类（如果指定了新分类）
                    if category and category not in paper.categories.all():
                        paper.categories.add(category)
                        
                    action_message = f"成功向现有试卷\"{paper_title}\"添加了 {len(imported_questions)} 道题目"
                    
                else:
                    # 创建新试卷
                    paper = ExamPaper.objects.create(
                        title=paper_title,
                        description=description,
                        duration=duration,
                        total_score=total_score or sum(q.score for q in imported_questions),
                        question_count=len(imported_questions),
                        paper_type='fixed',
                        use_import_order=use_import_order,
                        is_active=True,
                        created_by=request.user
                    )
                    
                    # 建立试卷题目关联
                    for i, question in enumerate(imported_questions):
                        ExamPaperQuestion.objects.create(
                            paper=paper,
                            question=question,
                            order=i + 1,
                            score=question.score
                        )
                    
                    # 关联分类
                    if category:
                        paper.categories.add(category)
                        
                    action_message = f"成功创建新试卷\"{paper_title}\"，包含 {len(imported_questions)} 道题目"
                
                return self.success({
                    'message': action_message,
                    'paper_id': paper.id,
                    'paper_title': paper.title,
                    'imported_questions': len(imported_questions),
                    'logs': importer.import_log
                })
                    
        except json.JSONDecodeError:
            return self.error("JSON数据格式错误")
        except Exception as e:
            logger.exception(f"导入试卷失败: {e}")
            return self.error(f"导入失败: {str(e)}")
    
    def _convert_frontend_question_format(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换前端题目数据格式为后端期望格式
        """
        converted = {}
        
        # 转换题目内容
        if 'question' in question_data:
            converted['title'] = question_data['question'][:200]  # 限制标题长度
            converted['description'] = question_data['question']
        else:
            converted['title'] = '未知题目'
            converted['description'] = ''
        
        # 转换题目类型（支持从JSON中读取type字段）
        converted['question_type'] = question_data.get('type', 'single')
        
        # 转换选项格式 - 将前端字符串数组转换为后端期望的对象数组格式
        if 'options' in question_data and isinstance(question_data['options'], list):
            # 前端发送的是字符串数组，需要转换为 [{"key": "A", "text": "选项内容"}, ...] 格式
            converted_options = []
            for i, option_text in enumerate(question_data['options']):
                option_key = chr(ord('A') + i)  # A, B, C, D...
                converted_options.append({
                    "key": option_key,
                    "text": str(option_text).strip()
                })
            converted['options'] = converted_options
        else:
            converted['options'] = []
        
        # 转换答案格式 - 使用'answer'字段，转换为字符串格式以符合验证器schema
        if 'correct' in question_data:
            correct_answer = question_data['correct']
            if isinstance(correct_answer, str):
                # 如果是字母格式，转换为数字索引字符串
                if correct_answer.upper() in ['A', 'B', 'C', 'D', 'E', 'F']:
                    index = ord(correct_answer.upper()) - 65  # A->0, B->1, C->2, D->3
                    converted['answer'] = str(index)
                else:
                    # 如果是数字格式，确保是字符串
                    try:
                        index = int(correct_answer)
                        converted['answer'] = str(index)
                    except ValueError:
                        # 如果不能转换为数字，默认为"0"
                        converted['answer'] = "0"
            elif isinstance(correct_answer, int):
                # 如果是数字，转换为字符串
                converted['answer'] = str(correct_answer)
            else:
                converted['answer'] = "0"  # 默认答案
        else:
            converted['answer'] = "0"  # 默认答案
        
        # 其他字段
        converted['explanation'] = question_data.get('explanation', '')
        converted['score'] = question_data.get('score', 2)
        converted['difficulty'] = question_data.get('difficulty', 'easy').lower()
        
        return converted


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
            logger.info(f"接收到的请求数据: {data}")
            
            # 验证必需字段
            paper_id = data.get('paper_id')
            logger.info(f"提取的paper_id: {paper_id}, 类型: {type(paper_id)}")
            if not paper_id:
                return self.error("缺少试卷ID")
                
            # 确保paper_id是整数
            try:
                paper_id = int(paper_id)
            except (ValueError, TypeError):
                logger.error(f"paper_id类型转换失败: {paper_id}")
                return self.error("试卷ID格式错误")
            
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
            
            # 按标签筛选 - 只有当试卷明确设置了标签时才进行筛选
            if hasattr(paper, 'tags') and paper.tags.exists():
                tag_ids = list(paper.tags.values_list('id', flat=True))
                if tag_ids:  # 确保标签列表不为空
                    query = query.filter(tags__in=tag_ids)
            
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