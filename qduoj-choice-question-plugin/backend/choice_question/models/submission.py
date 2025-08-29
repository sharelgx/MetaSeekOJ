# -*- coding: utf-8 -*-
"""
选择题提交记录模型
"""

from django.db import models
from django.core.validators import MinValueValidator
from account.models import User
from .base import PluginBaseModel
from .question import ChoiceQuestion


class ChoiceQuestionSubmission(PluginBaseModel):
    """
    选择题提交记录模型
    """
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name="关联题目"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="提交用户"
    )
    
    selected_answer = models.CharField(
        max_length=10,
        verbose_name="用户选择的答案",
        help_text="单选题格式: A，多选题格式: A,B,C"
    )
    
    is_correct = models.BooleanField(
        verbose_name="是否正确"
    )
    
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="得分"
    )
    
    submit_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="提交时间"
    )
    
    time_spent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="答题用时（秒）"
    )
    
    # IP地址记录
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP地址"
    )
    
    # 用户代理
    user_agent = models.TextField(
        blank=True,
        verbose_name="用户代理"
    )
    
    class Meta:
        db_table = "choice_plugin_submission"
        verbose_name = "选择题提交记录"
        verbose_name_plural = "选择题提交记录"
        ordering = ['-submit_time']
        indexes = [
            models.Index(fields=['user', 'question']),
            models.Index(fields=['question', 'is_correct']),
            models.Index(fields=['submit_time']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.question.title[:30]} - {'正确' if self.is_correct else '错误'}"
    
    def save(self, *args, **kwargs):
        """
        重写save方法，自动计算得分
        """
        if self.is_correct:
            self.score = self.question.score
        else:
            self.score = 0
        
        super().save(*args, **kwargs)
        
        # 更新题目统计信息
        self.question.update_statistics(self.is_correct)
    
    @classmethod
    def get_user_statistics(cls, user):
        """
        获取用户答题统计
        """
        submissions = cls.objects.filter(user=user)
        total_count = submissions.count()
        correct_count = submissions.filter(is_correct=True).count()
        total_score = submissions.aggregate(
            total=models.Sum('score')
        )['total'] or 0
        
        return {
            'total_submissions': total_count,
            'correct_submissions': correct_count,
            'accuracy_rate': round((correct_count / total_count) * 100, 2) if total_count > 0 else 0,
            'total_score': total_score,
            'average_score': round(total_score / total_count, 2) if total_count > 0 else 0
        }
    
    @classmethod
    def get_question_statistics(cls, question):
        """
        获取题目答题统计
        """
        submissions = cls.objects.filter(question=question)
        total_count = submissions.count()
        correct_count = submissions.filter(is_correct=True).count()
        
        # 统计各选项的选择次数
        option_stats = {}
        for submission in submissions:
            answer = submission.selected_answer
            if answer in option_stats:
                option_stats[answer] += 1
            else:
                option_stats[answer] = 1
        
        return {
            'total_submissions': total_count,
            'correct_submissions': correct_count,
            'accuracy_rate': round((correct_count / total_count) * 100, 2) if total_count > 0 else 0,
            'option_statistics': option_stats
        }
    
    @classmethod
    def get_recent_submissions(cls, user, limit=10):
        """
        获取用户最近的提交记录
        """
        return cls.objects.filter(user=user).order_by('-submit_time')[:limit]