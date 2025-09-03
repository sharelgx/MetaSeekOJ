from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from ..models import ChoiceQuestion, ChoiceQuestionSubmission, WrongQuestion, Category, QuestionTag


class StatisticsCalculator:
    """
    统计计算工具类
    提供各种统计分析功能
    """
    
    def __init__(self):
        self.cache_timeout = 300  # 缓存5分钟
    
    def get_user_statistics(self, user, days: int = 30) -> Dict[str, Any]:
        """
        获取用户统计数据
        
        Args:
            user: 用户对象
            days: 统计天数
            
        Returns:
            用户统计数据
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 基础统计
        total_submissions = ChoiceQuestionSubmission.objects.filter(
            user=user,
            submit_time__gte=start_date
        ).count()
        
        correct_submissions = ChoiceQuestionSubmission.objects.filter(
            user=user,
            is_correct=True,
            submit_time__gte=start_date
        ).count()
        
        # 计算正确率
        accuracy_rate = (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        # 总分统计
        total_score = ChoiceQuestionSubmission.objects.filter(
            user=user,
            submit_time__gte=start_date
        ).aggregate(total=models.Sum('score'))['total'] or 0
        
        # 难度分布统计
        difficulty_stats = self._get_user_difficulty_stats(user, start_date, end_date)
        
        # 分类统计
        category_stats = self._get_user_category_stats(user, start_date, end_date)
        
        # 每日提交统计
        daily_stats = self._get_user_daily_stats(user, start_date, end_date)
        
        # 错题统计
        wrong_questions_count = WrongQuestion.objects.filter(
            user=user,
            is_mastered=False
        ).count()
        
        mastered_questions_count = WrongQuestion.objects.filter(
            user=user,
            is_mastered=True
        ).count()
        
        # 学习进度
        unique_questions_attempted = ChoiceQuestionSubmission.objects.filter(
            user=user,
            submit_time__gte=start_date
        ).values('question').distinct().count()
        
        return {
            'user_id': user.id,
            'username': user.username,
            'period_days': days,
            'basic_stats': {
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'accuracy_rate': round(accuracy_rate, 2),
                'total_score': total_score,
                'unique_questions_attempted': unique_questions_attempted
            },
            'difficulty_distribution': difficulty_stats,
            'category_distribution': category_stats,
            'daily_activity': daily_stats,
            'wrong_questions': {
                'total_wrong': wrong_questions_count,
                'mastered': mastered_questions_count,
                'mastery_rate': round((mastered_questions_count / (wrong_questions_count + mastered_questions_count) * 100) if (wrong_questions_count + mastered_questions_count) > 0 else 0, 2)
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def get_question_statistics(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取题目统计数据
        
        Args:
            question: 题目对象
            
        Returns:
            题目统计数据
        """
        submissions = ChoiceQuestionSubmission.objects.filter(question=question)
        
        total_submissions = submissions.count()
        correct_submissions = submissions.filter(is_correct=True).count()
        
        # 计算正确率
        accuracy_rate = (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        # 平均得分
        avg_score = submissions.aggregate(avg=Avg('score'))['avg'] or 0
        
        # 选项分析
        option_analysis = self._get_question_option_analysis(question)
        
        # 提交时间分布
        time_distribution = self._get_question_time_distribution(question)
        
        # 用户分布
        user_distribution = self._get_question_user_distribution(question)
        
        # 错误分析
        wrong_analysis = self._get_question_wrong_analysis(question)
        
        return {
            'question_id': question.question_id,
            'title': question.title,
            'basic_stats': {
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'accuracy_rate': round(accuracy_rate, 2),
                'average_score': round(avg_score, 2),
                'max_score': question.score
            },
            'option_analysis': option_analysis,
            'time_distribution': time_distribution,
            'user_distribution': user_distribution,
            'wrong_analysis': wrong_analysis,
            'difficulty_assessment': self._assess_question_difficulty(accuracy_rate),
            'generated_at': timezone.now().isoformat()
        }
    
    def get_overall_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取整体统计数据
        
        Args:
            days: 统计天数
            
        Returns:
            整体统计数据
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 题目统计
        total_questions = ChoiceQuestion.objects.filter(is_public=True).count()
        questions_by_difficulty = ChoiceQuestion.objects.filter(
            is_public=True
        ).values('difficulty').annotate(count=Count('id'))
        
        # 提交统计
        total_submissions = ChoiceQuestionSubmission.objects.filter(
            submit_time__gte=start_date
        ).count()
        
        correct_submissions = ChoiceQuestionSubmission.objects.filter(
            submit_time__gte=start_date,
            is_correct=True
        ).count()
        
        # 用户活跃度
        active_users = ChoiceQuestionSubmission.objects.filter(
            submit_time__gte=start_date
        ).values('user').distinct().count()
        
        # 分类统计
        category_stats = Category.objects.annotate(
            question_count=Count('choicequestion'),
            submission_count=Count('choicequestion__choicequestionsubmission')
        ).values('name', 'question_count', 'submission_count')
        
        # 标签统计
        tag_stats = QuestionTag.objects.annotate(
            question_count=Count('choicequestion')
        ).order_by('-question_count')[:10]
        
        # 每日统计
        daily_stats = self._get_overall_daily_stats(start_date, end_date)
        
        return {
            'period_days': days,
            'question_stats': {
                'total_questions': total_questions,
                'difficulty_distribution': {item['difficulty']: item['count'] for item in questions_by_difficulty}
            },
            'submission_stats': {
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'overall_accuracy_rate': round((correct_submissions / total_submissions * 100) if total_submissions > 0 else 0, 2)
            },
            'user_stats': {
                'active_users': active_users
            },
            'category_distribution': list(category_stats),
            'popular_tags': [{'name': tag.name, 'question_count': tag.question_count} for tag in tag_stats],
            'daily_activity': daily_stats,
            'generated_at': timezone.now().isoformat()
        }
    
    def get_learning_progress(self, user, category_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取学习进度
        
        Args:
            user: 用户对象
            category_id: 分类ID，可选
            
        Returns:
            学习进度数据
        """
        # 构建查询条件
        question_filter = Q(is_public=True)
        if category_id:
            question_filter &= Q(category_id=category_id)
        
        # 总题目数
        total_questions = ChoiceQuestion.objects.filter(question_filter).count()
        
        # 已尝试的题目
        attempted_questions = ChoiceQuestionSubmission.objects.filter(
            user=user,
            question__in=ChoiceQuestion.objects.filter(question_filter)
        ).values('question').distinct().count()
        
        # 已掌握的题目（正确率>=80%）
        mastered_questions = 0
        if attempted_questions > 0:
            question_accuracy = ChoiceQuestionSubmission.objects.filter(
                user=user,
                question__in=ChoiceQuestion.objects.filter(question_filter)
            ).values('question').annotate(
                total=Count('id'),
                correct=Count('id', filter=Q(is_correct=True))
            ).annotate(
                accuracy=F('correct') * 100.0 / F('total')
            ).filter(accuracy__gte=80)
            
            mastered_questions = question_accuracy.count()
        
        # 错题数量
        wrong_questions = WrongQuestion.objects.filter(
            user=user,
            is_mastered=False
        )
        if category_id:
            wrong_questions = wrong_questions.filter(question__category_id=category_id)
        wrong_count = wrong_questions.count()
        
        # 计算进度百分比
        progress_percentage = (mastered_questions / total_questions * 100) if total_questions > 0 else 0
        
        # 难度分布进度
        difficulty_progress = {}
        for difficulty in ['easy', 'medium', 'hard']:
            diff_filter = question_filter & Q(difficulty=difficulty)
            diff_total = ChoiceQuestion.objects.filter(diff_filter).count()
            
            if diff_total > 0:
                diff_attempted = ChoiceQuestionSubmission.objects.filter(
                    user=user,
                    question__in=ChoiceQuestion.objects.filter(diff_filter)
                ).values('question').distinct().count()
                
                diff_mastered = 0
                if diff_attempted > 0:
                    diff_accuracy = ChoiceQuestionSubmission.objects.filter(
                        user=user,
                        question__in=ChoiceQuestion.objects.filter(diff_filter)
                    ).values('question').annotate(
                        total=Count('id'),
                        correct=Count('id', filter=Q(is_correct=True))
                    ).annotate(
                        accuracy=F('correct') * 100.0 / F('total')
                    ).filter(accuracy__gte=80)
                    
                    diff_mastered = diff_accuracy.count()
                
                difficulty_progress[difficulty] = {
                    'total': diff_total,
                    'attempted': diff_attempted,
                    'mastered': diff_mastered,
                    'progress': (diff_mastered / diff_total * 100) if diff_total > 0 else 0
                }
        
        return {
            'user_id': user.id,
            'category_id': category_id,
            'overall_progress': {
                'total_questions': total_questions,
                'attempted_questions': attempted_questions,
                'mastered_questions': mastered_questions,
                'wrong_questions': wrong_count,
                'progress_percentage': round(progress_percentage, 2)
            },
            'difficulty_progress': difficulty_progress,
            'recommendations': self._get_learning_recommendations(user, difficulty_progress, wrong_count),
            'generated_at': timezone.now().isoformat()
        }
    
    def _get_user_difficulty_stats(self, user, start_date, end_date) -> Dict[str, Any]:
        """
        获取用户难度分布统计
        """
        difficulty_stats = ChoiceQuestionSubmission.objects.filter(
            user=user,
            submit_time__gte=start_date,
            submit_time__lte=end_date
        ).values('question__difficulty').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).annotate(
            accuracy=F('correct') * 100.0 / F('total')
        )
        
        result = {}
        for stat in difficulty_stats:
            difficulty = stat['question__difficulty']
            result[difficulty] = {
                'total_submissions': stat['total'],
                'correct_submissions': stat['correct'],
                'accuracy_rate': round(stat['accuracy'], 2)
            }
        
        return result
    
    def _get_user_category_stats(self, user, start_date, end_date) -> List[Dict[str, Any]]:
        """
        获取用户分类统计
        """
        category_stats = ChoiceQuestionSubmission.objects.filter(
            user=user,
            submit_time__gte=start_date,
            submit_time__lte=end_date
        ).values('question__category__name').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).annotate(
            accuracy=F('correct') * 100.0 / F('total')
        ).order_by('-total')
        
        return [{
            'category_name': stat['question__category__name'] or '未分类',
            'total_submissions': stat['total'],
            'correct_submissions': stat['correct'],
            'accuracy_rate': round(stat['accuracy'], 2)
        } for stat in category_stats]
    
    def _get_user_daily_stats(self, user, start_date, end_date) -> List[Dict[str, Any]]:
        """
        获取用户每日统计
        """
        daily_stats = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            next_date = current_date + timedelta(days=1)
            
            day_submissions = ChoiceQuestionSubmission.objects.filter(
                user=user,
                submit_time__date=current_date
            )
            
            total = day_submissions.count()
            correct = day_submissions.filter(is_correct=True).count()
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'total_submissions': total,
                'correct_submissions': correct,
                'accuracy_rate': round((correct / total * 100) if total > 0 else 0, 2)
            })
            
            current_date = next_date
        
        return daily_stats
    
    def _get_question_option_analysis(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取题目选项分析
        """
        try:
            options = json.loads(question.options) if question.options else []
            correct_answer = json.loads(question.answer) if question.answer else []
        except (json.JSONDecodeError, TypeError):
            return {}
        
        submissions = ChoiceQuestionSubmission.objects.filter(question=question)
        total_submissions = submissions.count()
        
        option_stats = {}
        for i, option in enumerate(options):
            selection_count = 0
            
            for submission in submissions:
                try:
                    user_answer = json.loads(submission.user_answer)
                    if i in user_answer:
                        selection_count += 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            option_stats[f'option_{i}'] = {
                'text': option,
                'selection_count': selection_count,
                'selection_rate': round((selection_count / total_submissions * 100) if total_submissions > 0 else 0, 2),
                'is_correct': i in correct_answer
            }
        
        return option_stats
    
    def _get_question_time_distribution(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取题目时间分布
        """
        submissions = ChoiceQuestionSubmission.objects.filter(question=question)
        
        # 按小时分布
        hourly_stats = submissions.extra(
            select={'hour': 'EXTRACT(hour FROM submit_time)'}
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # 按星期分布
        weekly_stats = submissions.extra(
            select={'weekday': 'EXTRACT(dow FROM submit_time)'}
        ).values('weekday').annotate(count=Count('id')).order_by('weekday')
        
        return {
            'hourly_distribution': {int(stat['hour']): stat['count'] for stat in hourly_stats},
            'weekly_distribution': {int(stat['weekday']): stat['count'] for stat in weekly_stats}
        }
    
    def _get_question_user_distribution(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取题目用户分布
        """
        submissions = ChoiceQuestionSubmission.objects.filter(question=question)
        
        unique_users = submissions.values('user').distinct().count()
        repeat_users = submissions.values('user').annotate(
            submission_count=Count('id')
        ).filter(submission_count__gt=1).count()
        
        return {
            'unique_users': unique_users,
            'repeat_users': repeat_users,
            'repeat_rate': round((repeat_users / unique_users * 100) if unique_users > 0 else 0, 2)
        }
    
    def _get_question_wrong_analysis(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取题目错误分析
        """
        wrong_records = WrongQuestion.objects.filter(question=question)
        
        total_wrong_users = wrong_records.count()
        mastered_users = wrong_records.filter(is_mastered=True).count()
        
        # 错误类型分布
        error_types = wrong_records.values('error_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_wrong_users': total_wrong_users,
            'mastered_users': mastered_users,
            'mastery_rate': round((mastered_users / total_wrong_users * 100) if total_wrong_users > 0 else 0, 2),
            'error_type_distribution': {item['error_type']: item['count'] for item in error_types}
        }
    
    def _get_overall_daily_stats(self, start_date, end_date) -> List[Dict[str, Any]]:
        """
        获取整体每日统计
        """
        daily_stats = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_submissions = ChoiceQuestionSubmission.objects.filter(
                submit_time__date=current_date
            )
            
            total = day_submissions.count()
            correct = day_submissions.filter(is_correct=True).count()
            unique_users = day_submissions.values('user').distinct().count()
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'total_submissions': total,
                'correct_submissions': correct,
                'unique_users': unique_users,
                'accuracy_rate': round((correct / total * 100) if total > 0 else 0, 2)
            })
            
            current_date += timedelta(days=1)
        
        return daily_stats
    
    def _assess_question_difficulty(self, accuracy_rate: float) -> str:
        """
        评估题目难度
        """
        if accuracy_rate >= 80:
            return 'easy'
        elif accuracy_rate >= 50:
            return 'medium'
        else:
            return 'hard'
    
    def _get_learning_recommendations(self, user, difficulty_progress: Dict, wrong_count: int) -> List[str]:
        """
        获取学习建议
        """
        recommendations = []
        
        # 基于难度进度的建议
        if difficulty_progress.get('easy', {}).get('progress', 0) < 80:
            recommendations.append('建议先完成简单题目，巩固基础知识')
        
        if difficulty_progress.get('medium', {}).get('progress', 0) < 60:
            recommendations.append('可以尝试更多中等难度题目，提升解题能力')
        
        if difficulty_progress.get('hard', {}).get('progress', 0) < 40 and \
           difficulty_progress.get('medium', {}).get('progress', 0) > 70:
            recommendations.append('基础扎实，可以挑战困难题目')
        
        # 基于错题的建议
        if wrong_count > 10:
            recommendations.append('错题较多，建议重点复习错题本')
        elif wrong_count > 5:
            recommendations.append('适当复习错题，加深理解')
        
        if not recommendations:
            recommendations.append('学习进度良好，继续保持')
        
        return recommendations