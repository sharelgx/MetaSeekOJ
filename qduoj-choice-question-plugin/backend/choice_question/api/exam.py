# -*- coding: utf-8 -*-
"""
试卷相关API
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import (
    ExamPaper,
    ExamPaperQuestion,
    ExamSession,
    ChoiceQuestion,
    Category
)
from ..serializers import (
    ExamPaperListSerializer,
    ExamPaperDetailSerializer,
    ExamPaperCreateSerializer,
    ExamSessionListSerializer,
    ExamSessionDetailSerializer,
    ExamSessionCreateSerializer,
    ExamSubmitSerializer
)


@api_view(['GET', 'POST'])
def exam_paper_list(request):
    """
    试卷列表API
    GET: 获取试卷列表
    POST: 创建试卷
    """
    if request.method == 'GET':
        # 获取查询参数
        category_id = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        question_type = request.GET.get('question_type')
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 构建查询条件
        queryset = ExamPaper.objects.filter(
            is_active=True,
            is_public=True
        ).select_related('category', 'created_by')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if difficulty and difficulty != 'mixed':
            queryset = queryset.filter(difficulty_filter=difficulty)
        
        if question_type and question_type != 'mixed':
            queryset = queryset.filter(question_type_filter=question_type)
        
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        serializer = ExamPaperListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages
            }
        })
    
    elif request.method == 'POST':
        # 创建试卷（需要登录）
        if not request.user.is_authenticated:
            return Response({
                'code': 401,
                'message': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ExamPaperCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # 创建试卷
                exam_paper = serializer.save(created_by=request.user)
                
                # 生成试卷题目
                questions = exam_paper.generate_questions()
                
                if not questions:
                    return Response({
                        'code': 400,
                        'message': '没有找到符合条件的题目'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 返回创建的试卷详情
                detail_serializer = ExamPaperDetailSerializer(exam_paper)
                return Response({
                    'code': 0,
                    'message': '试卷创建成功',
                    'data': detail_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def exam_paper_detail(request, paper_id):
    """
    试卷详情API
    """
    exam_paper = get_object_or_404(
        ExamPaper,
        id=paper_id,
        is_active=True,
        is_public=True
    )
    
    serializer = ExamPaperDetailSerializer(exam_paper)
    return Response({
        'code': 0,
        'message': 'success',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exam_session_create(request):
    """
    创建考试会话
    """
    serializer = ExamSessionCreateSerializer(data=request.data)
    if serializer.is_valid():
        exam_paper = serializer.validated_data['exam_paper']
        
        # 检查用户是否已有进行中的考试
        existing_session = ExamSession.objects.filter(
            user=request.user,
            exam_paper=exam_paper,
            status__in=['not_started', 'in_progress']
        ).first()
        
        if existing_session:
            # 返回现有会话
            detail_serializer = ExamSessionDetailSerializer(existing_session)
            return Response({
                'code': 0,
                'message': '已存在考试会话',
                'data': detail_serializer.data
            })
        
        # 创建新的考试会话
        exam_session = ExamSession.objects.create(
            exam_paper=exam_paper,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        detail_serializer = ExamSessionDetailSerializer(exam_session)
        return Response({
            'code': 0,
            'message': '考试会话创建成功',
            'data': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'code': 400,
        'message': '数据验证失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exam_session_start(request, session_id):
    """
    开始考试
    """
    exam_session = get_object_or_404(
        ExamSession,
        id=session_id,
        user=request.user
    )
    
    if exam_session.status != 'not_started':
        return Response({
            'code': 400,
            'message': '考试已开始或已结束'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 开始考试
    exam_session.start_exam()
    
    serializer = ExamSessionDetailSerializer(exam_session)
    return Response({
        'code': 0,
        'message': '考试开始',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_session_detail(request, session_id):
    """
    获取考试会话详情
    """
    exam_session = get_object_or_404(
        ExamSession,
        id=session_id,
        user=request.user
    )
    
    # 检查是否超时
    if exam_session.status == 'in_progress':
        exam_session.check_timeout()
    
    serializer = ExamSessionDetailSerializer(exam_session)
    return Response({
        'code': 0,
        'message': 'success',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exam_session_answer(request, session_id):
    """
    提交单题答案
    """
    exam_session = get_object_or_404(
        ExamSession,
        id=session_id,
        user=request.user
    )
    
    if exam_session.status != 'in_progress':
        return Response({
            'code': 400,
            'message': '考试未进行中'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查是否超时
    if exam_session.check_timeout():
        return Response({
            'code': 400,
            'message': '考试时间已到'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    question_id = request.data.get('question_id')
    answer = request.data.get('answer')
    
    if not question_id or not answer:
        return Response({
            'code': 400,
            'message': '题目ID和答案不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证题目是否属于当前试卷
    paper_question = get_object_or_404(
        ExamPaperQuestion,
        exam_paper=exam_session.exam_paper,
        question_id=question_id
    )
    
    # 判断答案是否正确
    question = paper_question.question
    is_correct = question.check_answer(answer)
    score = paper_question.score if is_correct else 0
    
    # 保存答案
    if not exam_session.answers:
        exam_session.answers = {}
    
    exam_session.answers[str(question_id)] = {
        'answer': answer,
        'is_correct': is_correct,
        'score': score,
        'submit_time': timezone.now().isoformat()
    }
    exam_session.save()
    
    return Response({
        'code': 0,
        'message': '答案提交成功',
        'data': {
            'is_correct': is_correct,
            'score': score
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exam_session_submit(request, session_id):
    """
    提交整张试卷
    """
    exam_session = get_object_or_404(
        ExamSession,
        id=session_id,
        user=request.user
    )
    
    if exam_session.status != 'in_progress':
        return Response({
            'code': 400,
            'message': '考试未进行中'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 处理批量答案提交
    serializer = ExamSubmitSerializer(data=request.data)
    if serializer.is_valid():
        answers_data = serializer.validated_data['answers']
        
        # 验证所有题目并计算分数
        if not exam_session.answers:
            exam_session.answers = {}
        
        for answer_item in answers_data:
            question_id = answer_item['question_id']
            answer = answer_item['answer']
            
            # 验证题目是否属于当前试卷
            try:
                paper_question = ExamPaperQuestion.objects.get(
                    exam_paper=exam_session.exam_paper,
                    question_id=question_id
                )
                
                # 判断答案是否正确
                question = paper_question.question
                is_correct = question.check_answer(answer)
                score = paper_question.score if is_correct else 0
                
                # 保存答案
                exam_session.answers[str(question_id)] = {
                    'answer': answer,
                    'is_correct': is_correct,
                    'score': score,
                    'submit_time': timezone.now().isoformat()
                }
                
            except ExamPaperQuestion.DoesNotExist:
                continue
        
        # 提交考试
        exam_session.submit_exam()
        
        serializer = ExamSessionDetailSerializer(exam_session)
        return Response({
            'code': 0,
            'message': '考试提交成功',
            'data': serializer.data
        })
    
    return Response({
        'code': 400,
        'message': '数据验证失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_session_list(request):
    """
    获取用户考试记录列表
    """
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status_filter = request.GET.get('status')
    
    queryset = ExamSession.objects.filter(
        user=request.user
    ).select_related('exam_paper', 'exam_paper__category')
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # 分页
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # 序列化数据
    serializer = ExamSessionListSerializer(page_obj.object_list, many=True)
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': {
            'results': serializer.data,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        }
    })


@api_view(['GET'])
def exam_paper_generate_preview(request):
    """
    预览试卷生成结果
    """
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty', 'mixed')
    question_type = request.GET.get('question_type', 'mixed')
    question_count = int(request.GET.get('question_count', 10))
    
    # 构建查询条件
    queryset = ChoiceQuestion.objects.filter(
        visible=True,
        is_public=True
    )
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    if difficulty != 'mixed':
        queryset = queryset.filter(difficulty=difficulty)
    
    if question_type != 'mixed':
        queryset = queryset.filter(question_type=question_type)
    
    available_count = queryset.count()
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': {
            'available_count': available_count,
            'requested_count': question_count,
            'can_generate': available_count >= question_count
        }
    })