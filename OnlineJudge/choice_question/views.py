from django.db.models import Q, F
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import action
from rest_framework import status
from utils.api import CSRFExemptAPIView, validate_serializer
from account.decorators import login_required, super_admin_required
from .models import (
    Category,
    QuestionTag,
    ChoiceQuestion,
    ChoiceQuestionSubmission,
    WrongQuestion
)
from .serializers import (
    ChoiceQuestionCategorySerializer,
    ChoiceQuestionTagSerializer,
    ChoiceQuestionListSerializer,
    ChoiceQuestionDetailSerializer,
    ChoiceQuestionCreateSerializer,
    ChoiceQuestionSubmissionSerializer,
    ChoiceQuestionSubmissionCreateSerializer,
    WrongQuestionSerializer
)


class ChoiceQuestionCategoryAPI(CSRFExemptAPIView):
    """选择题分类API"""
    
    def paginate_queryset(self, request, queryset, serializer_class):
        """标准DRF分页格式"""
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        
        try:
            page_size = int(request.GET.get('page_size', 20))
        except ValueError:
            page_size = 20
        
        if page_size > 100:
            page_size = 100
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        serialized_data = serializer_class(page_obj.object_list, many=True).data
        
        return {
            'results': serialized_data,
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None
        }
    
    def get(self, request):
        """获取分类列表"""
        categories = Category.objects.all().order_by('name')
        return self.success(self.paginate_queryset(request, categories, ChoiceQuestionCategorySerializer))
    
    @super_admin_required
    def post(self, request, pk=None):
        """创建分类"""
        serializer = ChoiceQuestionCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return self.success(ChoiceQuestionCategorySerializer(category).data)
        return self.error(msg="数据验证失败", err=serializer.errors)
    
    @super_admin_required
    def put(self, request, pk=None):
        """更新分类"""
        try:
            category = Category.objects.get(pk=pk)
            serializer = ChoiceQuestionCategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success(serializer.data)
            return self.error(msg="数据验证失败", err=serializer.errors)
        except Category.DoesNotExist:
            return self.error(msg="分类不存在")
    
    @super_admin_required
    def patch(self, request, pk=None):
        """部分更新分类"""
        try:
            category = Category.objects.get(pk=pk)
            serializer = ChoiceQuestionCategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success(serializer.data)
            return self.error(msg="数据验证失败", err=serializer.errors)
        except Category.DoesNotExist:
            return self.error(msg="分类不存在")
    
    @super_admin_required
    def delete(self, request, pk=None):
        """删除分类"""
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "分类不存在"}, status=status.HTTP_404_NOT_FOUND)


class ChoiceQuestionTagAPI(CSRFExemptAPIView):
    """选择题标签API"""
    
    def paginate_queryset(self, request, queryset, serializer_class):
        """分页处理"""
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        serializer = serializer_class(page_obj.object_list, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None
        }
    
    def get(self, request):
        """获取标签列表"""
        tags = QuestionTag.objects.all().order_by('name')
        return self.success(self.paginate_queryset(request, tags, ChoiceQuestionTagSerializer))
    
    @super_admin_required
    def post(self, request, pk=None):
        """创建标签"""
        serializer = ChoiceQuestionTagSerializer(data=request.data)
        if serializer.is_valid():
            tag = serializer.save()
            return Response(ChoiceQuestionTagSerializer(tag).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoiceQuestionAPI(CSRFExemptAPIView):
    """选择题API"""
    
    def paginate_queryset(self, request, queryset, serializer_class):
        """分页处理"""
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        serializer = serializer_class(page_obj.object_list, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None
        }
    
    def get(self, request):
        """获取选择题列表"""
        questions = ChoiceQuestion.objects.select_related('category', 'created_by').prefetch_related('tags')
        
        # 筛选条件
        keyword = request.GET.get('keyword')
        if keyword:
            questions = questions.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        
        category_id = request.GET.get('category')
        if category_id:
            questions = questions.filter(category_id=category_id)
        
        tag_id = request.GET.get('tag')
        if tag_id:
            questions = questions.filter(tags__id=tag_id)
        
        difficulty = request.GET.get('difficulty')
        if difficulty:
            questions = questions.filter(difficulty=difficulty)
        
        question_type = request.GET.get('type')
        if question_type:
            questions = questions.filter(question_type=question_type)
        
        # 排序
        order_by = request.GET.get('order_by', '-create_time')
        questions = questions.order_by(order_by)
        
        return self.success(self.paginate_queryset(request, questions, ChoiceQuestionListSerializer))
    
    @super_admin_required
    @validate_serializer(ChoiceQuestionCreateSerializer)
    def post(self, request, pk=None):
        """创建选择题"""
        data = request.data
        data['created_by'] = request.user
        
        serializer = ChoiceQuestionCreateSerializer(data=data)
        if serializer.is_valid():
            question = serializer.save(created_by=request.user)
            return Response(ChoiceQuestionDetailSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoiceQuestionDetailAPI(CSRFExemptAPIView):
    """选择题详情API"""
    
    def get(self, request, pk=None):
        """获取选择题详情"""
        # 优先使用URL中的pk参数，其次使用查询参数中的id
        question_id = pk or request.GET.get('id')
        if not question_id:
            return Response({"error": "题目ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            question = ChoiceQuestion.objects.select_related(
                'category', 'created_by'
            ).prefetch_related('tags').get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return Response({"error": "题目不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 如果用户已登录，获取用户的提交状态
        user_submission = None
        if request.user.is_authenticated:
            try:
                user_submission = ChoiceQuestionSubmission.objects.get(
                    user=request.user, question=question
                )
            except ChoiceQuestionSubmission.DoesNotExist:
                pass
        
        data = ChoiceQuestionDetailSerializer(question).data
        if user_submission:
            data['user_submission'] = {
                'is_correct': user_submission.is_correct,
                'selected_answer': user_submission.selected_answer,
                'submit_time': user_submission.create_time
            }
        
        return Response(data)
    
    @super_admin_required
    def put(self, request, pk=None):
        """更新选择题"""
        question_id = pk or request.data.get('id')
        if not question_id:
            return Response({"error": "题目ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return Response({"error": "题目不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChoiceQuestionCreateSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            question = serializer.save()
            return Response(ChoiceQuestionDetailSerializer(question).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @super_admin_required
    def delete(self, request, pk=None):
        """删除选择题"""
        question_id = pk or request.data.get('id')
        if not question_id:
            return Response({"error": "题目ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChoiceQuestion.DoesNotExist:
            return Response({"error": "题目不存在"}, status=status.HTTP_404_NOT_FOUND)


class ChoiceQuestionSubmissionAPI(CSRFExemptAPIView):
    """选择题提交API"""
    
    def paginate_queryset(self, request, queryset, serializer_class):
        """分页处理"""
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        serializer = serializer_class(page_obj.object_list, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None
        }
    
    @login_required
    def get(self, request):
        """获取用户提交记录"""
        submissions = ChoiceQuestionSubmission.objects.filter(
            user=request.user
        ).select_related('question', 'question__category').order_by('-create_time')
        
        # 筛选条件
        question_id = request.GET.get('question_id')
        if question_id:
            submissions = submissions.filter(question__id=question_id)
        
        is_correct = request.GET.get('is_correct')
        if is_correct is not None:
            submissions = submissions.filter(is_correct=is_correct.lower() == 'true')
        
        return Response(self.paginate_queryset(request, submissions, ChoiceQuestionSubmissionSerializer))
    
    @login_required
    @validate_serializer(ChoiceQuestionSubmissionCreateSerializer)
    def post(self, request, pk=None):
        """提交答案"""
        question_id = request.data.get('question')
        selected_answer = request.data.get('selected_answer')
        
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return Response({"error": "题目不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否已经提交过
        existing_submission = ChoiceQuestionSubmission.objects.filter(
            user=request.user, question=question
        ).first()
        
        if existing_submission:
            return Response({"error": "您已经提交过该题目"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 判断答案是否正确
        is_correct = selected_answer in question.correct_answer
        score = question.score if is_correct else 0
        
        # 创建提交记录
        submission = ChoiceQuestionSubmission.objects.create(
            user=request.user,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct,
            score=score
        )
        
        # 更新题目统计
        question.total_submit = F('total_submit') + 1
        if is_correct:
            question.total_accepted = F('total_accepted') + 1
        question.save(update_fields=['total_submit', 'total_accepted'])
        
        # 如果答错了，添加到错题本
        if not is_correct:
            wrong_question, created = WrongQuestion.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={
                    'first_wrong_time': timezone.now(),
                    'last_wrong_answer': selected_answer
                }
            )
            if not created:
                # 如果已存在，更新最后错误答案
                wrong_question.last_wrong_answer = selected_answer
                wrong_question.save(update_fields=['last_wrong_answer'])
        
        return Response({
            'is_correct': is_correct,
            'score': score,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'submission_id': submission.id
        }, status=status.HTTP_200_OK)


class WrongQuestionAPI(CSRFExemptAPIView):
    """错题本API"""
    
    def paginate_queryset(self, request, queryset, serializer_class):
        """分页处理"""
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        serializer = serializer_class(page_obj.object_list, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None
        }
    
    @login_required
    def get(self, request):
        """获取错题本"""
        wrong_questions = WrongQuestion.objects.filter(
            user=request.user
        ).select_related('question', 'question__category').order_by('-first_wrong_time')
        
        # 筛选条件
        category_id = request.GET.get('category')
        if category_id:
            wrong_questions = wrong_questions.filter(question__category_id=category_id)
        
        difficulty = request.GET.get('difficulty')
        if difficulty:
            wrong_questions = wrong_questions.filter(question__difficulty=difficulty)
        
        return Response(self.paginate_queryset(request, wrong_questions, WrongQuestionSerializer))
    
    @login_required
    def delete(self, request, pk=None):
        """从错题本中移除"""
        if pk:
            # 通过URL参数删除特定错题记录
            try:
                wrong_question = WrongQuestion.objects.get(
                    id=pk, user=request.user
                )
                wrong_question.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except WrongQuestion.DoesNotExist:
                return Response({"error": "错题记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 通过请求体删除
            question_id = request.data.get('question_id')
            if not question_id:
                return Response({"error": "题目ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                wrong_question = WrongQuestion.objects.get(
                    user=request.user, question__id=question_id
                )
                wrong_question.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except WrongQuestion.DoesNotExist:
                return Response({"error": "错题记录不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    @login_required
    def post(self, request, pk=None):
        """标记错题为已掌握"""
        if not pk:
            return Response({"error": "错题ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wrong_question = WrongQuestion.objects.get(id=pk, user=request.user)
            wrong_question.mark_as_mastered()
            return Response({"message": "错题已标记为已掌握"}, status=status.HTTP_200_OK)
        except WrongQuestion.DoesNotExist:
            return Response({"error": "错题记录不存在"}, status=status.HTTP_404_NOT_FOUND)


class ChoiceQuestionStatsAPI(CSRFExemptAPIView):
    """选择题统计API"""
    
    @login_required
    def get(self, request):
        """获取用户统计信息"""
        user = request.user
        
        # 总题目数
        total_questions = ChoiceQuestion.objects.count()
        
        # 用户提交统计
        user_submissions = ChoiceQuestionSubmission.objects.filter(user=user)
        total_submitted = user_submissions.count()
        total_correct = user_submissions.filter(is_correct=True).count()
        
        # 错题数量
        wrong_count = WrongQuestion.objects.filter(user=user).count()
        
        # 按分类统计
        category_stats = []
        categories = Category.objects.all()
        for category in categories:
            category_total = ChoiceQuestion.objects.filter(category=category).count()
            category_submitted = user_submissions.filter(question__category=category).count()
            category_correct = user_submissions.filter(
                question__category=category, is_correct=True
            ).count()
            
            category_stats.append({
                'category': ChoiceQuestionCategorySerializer(category).data,
                'total': category_total,
                'submitted': category_submitted,
                'correct': category_correct,
                'accuracy': round(category_correct / category_submitted * 100, 2) if category_submitted > 0 else 0
            })
        
        return Response({
            'total_questions': total_questions,
            'total_submitted': total_submitted,
            'total_correct': total_correct,
            'wrong_count': wrong_count,
            'accuracy': round(total_correct / total_submitted * 100, 2) if total_submitted > 0 else 0,
            'category_stats': category_stats
        })
