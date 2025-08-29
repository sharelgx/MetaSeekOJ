# -*- coding: utf-8 -*-
"""
选择题统计分析API视图
"""

from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from utils.api import APIView
from account.decorators import login_required, super_admin_required
from ..models import ChoiceQuestion, ChoiceQuestionSubmission, WrongQuestion, Category, QuestionTag
from ..utils.statistics import QuestionStatistics, UserStatistics, SystemStatistics


class OverallStatisticsAPI(APIView):
    """
    总体统计API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取系统总体统计信息
        """
        statistics = SystemStatistics.get_overall_statistics()
        return self.success(statistics)


class UserStatisticsAPI(APIView):
    """
    用户统计API
    """
    
    @login_required
    def get(self, request, user_id=None):
        """
        获取用户统计信息
        """
        # 如果没有指定用户ID，则获取当前用户的统计
        if user_id is None:
            target_user = request.user
        else:
            # 只有管理员可以查看其他用户的统计
            if not request.user.is_admin():
                return self.error("无权限查看其他用户统计", status_code=403)
            
            from account.models import User
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.error("用户不存在", status_code=404)
        
        statistics = UserStatistics.get_user_statistics(target_user)
        return self.success(statistics)


class QuestionStatisticsDetailAPI(APIView):
    """
    题目详细统计API
    """
    
    @super_admin_required
    def get(self, request, question_id):
        """
        获取题目详细统计信息
        """
        try:
            question = ChoiceQuestion.objects.get(id=question_id)
        except ChoiceQuestion.DoesNotExist:
            return self.error("题目不存在", status_code=404)
        
        statistics = QuestionStatistics.get_detailed_statistics(question)
        return self.success(statistics)


class CategoryStatisticsAPI(APIView):
    """
    分类统计API
    """
    
    def get(self, request):
        """
        获取分类统计信息
        """
        # 获取所有分类的统计信息
        categories = Category.objects.filter(is_active=True)
        category_stats = []
        
        for category in categories:
            questions = category.get_all_questions()
            total_submissions = sum(q.total_submit for q in questions)
            total_accepted = sum(q.total_accepted for q in questions)
            
            stats = {
                'id': category.id,
                'name': category.name,
                'full_name': category.get_full_name(),
                'question_count': questions.count(),
                'total_submissions': total_submissions,
                'total_accepted': total_accepted,
                'acceptance_rate': round(total_accepted / total_submissions * 100, 2) if total_submissions > 0 else 0,
                'difficulty_distribution': {
                    'easy': questions.filter(difficulty='easy').count(),
                    'medium': questions.filter(difficulty='medium').count(),
                    'hard': questions.filter(difficulty='hard').count(),
                }
            }
            category_stats.append(stats)
        
        # 按题目数量排序
        category_stats.sort(key=lambda x: x['question_count'], reverse=True)
        
        return self.success(category_stats)


class DifficultyStatisticsAPI(APIView):
    """
    难度统计API
    """
    
    def get(self, request):
        """
        获取难度分布统计
        """
        difficulty_stats = []
        
        for difficulty, difficulty_name in ChoiceQuestion.DIFFICULTY_CHOICES:
            questions = ChoiceQuestion.objects.filter(difficulty=difficulty, visible=True)
            total_submissions = sum(q.total_submit for q in questions)
            total_accepted = sum(q.total_accepted for q in questions)
            
            stats = {
                'difficulty': difficulty,
                'difficulty_name': difficulty_name,
                'question_count': questions.count(),
                'total_submissions': total_submissions,
                'total_accepted': total_accepted,
                'acceptance_rate': round(total_accepted / total_submissions * 100, 2) if total_submissions > 0 else 0,
                'avg_score': questions.aggregate(avg_score=Avg('score'))['avg_score'] or 0
            }
            difficulty_stats.append(stats)
        
        return self.success(difficulty_stats)


class SubmissionTrendAPI(APIView):
    """
    提交趋势API
    """
    
    def get(self, request):
        """
        获取提交趋势数据
        """
        # 获取时间范围参数
        days = int(request.GET.get('days', 30))
        days = min(days, 365)  # 最多一年
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 按日期统计提交数据
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 当日提交统计
            daily_submissions = ChoiceQuestionSubmission.objects.filter(
                submit_time__date=current_date
            )
            
            total_count = daily_submissions.count()
            correct_count = daily_submissions.filter(is_correct=True).count()
            unique_users = daily_submissions.values('user').distinct().count()
            
            daily_stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_submissions': total_count,
                'correct_submissions': correct_count,
                'wrong_submissions': total_count - correct_count,
                'unique_users': unique_users,
                'accuracy_rate': round(correct_count / total_count * 100, 2) if total_count > 0 else 0
            })
            
            current_date = next_date
        
        return self.success(daily_stats)


class PopularQuestionsAPI(APIView):
    """
    热门题目API
    """
    
    def get(self, request):
        """
        获取热门题目列表
        """
        limit = int(request.GET.get('limit', 20))
        limit = min(limit, 100)
        
        sort_by = request.GET.get('sort_by', 'submissions')  # submissions, acceptance_rate, difficulty
        
        questions = ChoiceQuestion.objects.filter(visible=True, is_public=True)
        
        if sort_by == 'submissions':
            questions = questions.order_by('-total_submit')
        elif sort_by == 'acceptance_rate':
            # 只考虑有提交的题目
            questions = questions.filter(total_submit__gt=0).extra(
                select={'acceptance_rate': 'total_accepted * 100.0 / total_submit'}
            ).order_by('-acceptance_rate')
        elif sort_by == 'difficulty':
            # 按难度和提交数排序
            questions = questions.order_by('difficulty', '-total_submit')
        
        questions = questions[:limit]
        
        popular_questions = []
        for question in questions:
            popular_questions.append({
                'id': question.id,
                '_id': question._id,
                'title': question.title,
                'difficulty': question.get_difficulty_display(),
                'category': question.category.name if question.category else None,
                'total_submit': question.total_submit,
                'total_accepted': question.total_accepted,
                'acceptance_rate': question.acceptance_rate,
                'score': question.score,
                'create_time': question.create_time
            })
        
        return self.success(popular_questions)


class WrongQuestionAnalysisAPI(APIView):
    """
    错题分析API
    """
    
    @login_required
    def get(self, request):
        """
        获取用户错题分析
        """
        user_wrong_questions = WrongQuestion.objects.filter(user=request.user)
        
        # 错误类型分布
        error_type_stats = []
        for error_type, error_type_name in WrongQuestion.ERROR_TYPE_CHOICES:
            count = user_wrong_questions.filter(error_type=error_type).count()
            error_type_stats.append({
                'error_type': error_type,
                'error_type_name': error_type_name,
                'count': count
            })
        
        # 难度分布
        difficulty_stats = []
        for difficulty, difficulty_name in ChoiceQuestion.DIFFICULTY_CHOICES:
            count = user_wrong_questions.filter(question__difficulty=difficulty).count()
            difficulty_stats.append({
                'difficulty': difficulty,
                'difficulty_name': difficulty_name,
                'count': count
            })
        
        # 分类分布
        category_stats = []
        categories = Category.objects.filter(
            id__in=user_wrong_questions.values_list('question__category', flat=True)
        ).distinct()
        
        for category in categories:
            if category:
                count = user_wrong_questions.filter(question__category=category).count()
                category_stats.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'count': count
                })
        
        # 时间趋势（最近30天）
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        time_trend = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = user_wrong_questions.filter(
                first_wrong_time__date=current_date
            ).count()
            
            time_trend.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            
            current_date = next_date
        
        analysis = {
            'total_wrong_questions': user_wrong_questions.count(),
            'mastered_count': user_wrong_questions.filter(is_mastered=True).count(),
            'unmastered_count': user_wrong_questions.filter(is_mastered=False).count(),
            'error_type_distribution': error_type_stats,
            'difficulty_distribution': difficulty_stats,
            'category_distribution': category_stats,
            'time_trend': time_trend
        }
        
        return self.success(analysis)


class SystemHealthAPI(APIView):
    """
    系统健康状态API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取系统健康状态
        """
        # 数据完整性检查
        total_questions = ChoiceQuestion.objects.count()
        questions_without_category = ChoiceQuestion.objects.filter(category=None).count()
        questions_without_tags = ChoiceQuestion.objects.filter(tags=None).count()
        
        # 统计数据一致性检查
        inconsistent_categories = []
        for category in Category.objects.all():
            actual_count = category.choicequestion_set.count()
            if category.question_count != actual_count:
                inconsistent_categories.append({
                    'id': category.id,
                    'name': category.name,
                    'recorded_count': category.question_count,
                    'actual_count': actual_count
                })
        
        inconsistent_tags = []
        for tag in QuestionTag.objects.all():
            actual_count = tag.choicequestion_set.count()
            if tag.question_count != actual_count:
                inconsistent_tags.append({
                    'id': tag.id,
                    'name': tag.name,
                    'recorded_count': tag.question_count,
                    'actual_count': actual_count
                })
        
        # 最近活动
        recent_submissions = ChoiceQuestionSubmission.objects.filter(
            submit_time__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        recent_wrong_questions = WrongQuestion.objects.filter(
            last_wrong_time__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        health_status = {
            'data_integrity': {
                'total_questions': total_questions,
                'questions_without_category': questions_without_category,
                'questions_without_tags': questions_without_tags,
                'category_percentage': round((total_questions - questions_without_category) / total_questions * 100, 2) if total_questions > 0 else 0,
                'tag_percentage': round((total_questions - questions_without_tags) / total_questions * 100, 2) if total_questions > 0 else 0
            },
            'data_consistency': {
                'inconsistent_categories': inconsistent_categories,
                'inconsistent_tags': inconsistent_tags,
                'categories_need_update': len(inconsistent_categories),
                'tags_need_update': len(inconsistent_tags)
            },
            'recent_activity': {
                'submissions_24h': recent_submissions,
                'wrong_questions_24h': recent_wrong_questions
            },
            'overall_health': 'good' if len(inconsistent_categories) == 0 and len(inconsistent_tags) == 0 else 'warning'
        }
        
        return self.success(health_status)