# -*- coding: utf-8 -*-
"""
试卷和考试会话模型
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from .base import PluginBaseModel
from .question import ChoiceQuestion
from .category import Category
from .tag import QuestionTag
from utils.models import JSONField
import json


class ExamPaper(PluginBaseModel):
    """
    试卷模型
    """
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="试卷标题")
    description = models.TextField(blank=True, verbose_name="试卷描述")
    duration = models.IntegerField(verbose_name="考试时长(分钟)")
    total_score = models.IntegerField(default=100, verbose_name="总分")
    
    # 题目配置
    question_count = models.IntegerField(verbose_name="题目数量")
    categories = models.ManyToManyField(Category, blank=True, verbose_name="题目分类")
    tags = models.ManyToManyField(QuestionTag, blank=True, verbose_name="题目标签")
    difficulty_distribution = JSONField(
        default=dict, 
        verbose_name="难度分布",
        help_text="格式: {'easy': 5, 'medium': 3, 'hard': 2}"
    )
    
    # 试卷状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    use_import_order = models.BooleanField(
        default=False, 
        help_text='是否按题目导入顺序显示题目，适用于整套试卷导入的场景', 
        verbose_name='按导入顺序排序'
    )
    
    # 试卷类型
    PAPER_TYPE_CHOICES = [
        ('dynamic', '动态生成'),
        ('fixed', '固定题目'),
    ]
    
    paper_type = models.CharField(
        max_length=20,
        choices=PAPER_TYPE_CHOICES,
        default='dynamic',
        verbose_name="试卷类型",
        help_text="动态生成：根据配置随机生成题目；固定题目：使用导入的固定题目集合"
    )
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")
    
    class Meta:
        db_table = "choice_exam_paper"
        verbose_name = "试卷"
        verbose_name_plural = "试卷"
        ordering = ['-create_time']
    
    def __str__(self):
        return self.title
    
    def generate_questions(self):
        """
        根据配置生成试卷题目
        """
        questions = []
        
        # 获取基础查询集
        queryset = ChoiceQuestion.objects.filter(is_public=True)
        
        # 按分类筛选（包含子分类）
        if self.categories.exists():
            all_categories = []
            for category in self.categories.all():
                # 获取当前分类及其所有子分类
                descendant_categories = category.get_descendants(include_self=True)
                all_categories.extend(descendant_categories)
            queryset = queryset.filter(category__in=all_categories)
        
        # 按标签筛选
        if self.tags.exists():
            queryset = queryset.filter(tags__in=self.tags.all()).distinct()
        
        # 按难度分布生成题目
        for difficulty, count in self.difficulty_distribution.items():
            if count > 0:
                difficulty_questions = queryset.filter(difficulty=difficulty).order_by('?')[:count]
                questions.extend(list(difficulty_questions))
        
        # 如果按难度分布生成的题目不够，随机补充
        if len(questions) < self.question_count:
            remaining_count = self.question_count - len(questions)
            existing_ids = [q.id for q in questions]
            additional_questions = queryset.exclude(id__in=existing_ids).order_by('?')[:remaining_count]
            questions.extend(list(additional_questions))
        
        return questions[:self.question_count]
    
    def get_questions(self):
        """获取试卷题目，支持两种模式"""
        if self.paper_type == 'fixed':
            # 固定题目模式：从关联表获取
            return ChoiceQuestion.objects.filter(
                paper_questions__paper=self
            ).order_by('paper_questions__order')
        else:
            # 动态生成模式：使用现有逻辑
            return self.generate_questions()


class ExamPaperQuestion(PluginBaseModel):
    """
    试卷题目关联模型
    """
    
    paper = models.ForeignKey(
        ExamPaper,
        on_delete=models.CASCADE,
        related_name="paper_questions",
        verbose_name="试卷"
    )
    
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        verbose_name="题目"
    )
    
    order = models.IntegerField(
        verbose_name="题目顺序"
    )
    
    score = models.IntegerField(
        default=2,
        verbose_name="题目分值"
    )
    
    class Meta:
        db_table = "choice_exam_paper_question"
        verbose_name = "试卷题目"
        verbose_name_plural = "试卷题目"
        ordering = ['order']
        unique_together = [['paper', 'question'], ['paper', 'order']]
        
    def __str__(self):
        return f"{self.paper.title} - 第{self.order}题"


class ExamSession(PluginBaseModel):
    """
    考试会话模型
    """
    STATUS_CHOICES = [
        ('created', '已创建'),
        ('started', '进行中'),
        ('submitted', '已提交'),
        ('timeout', '超时'),
    ]
    
    paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, verbose_name="试卷")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="考生")
    
    # 考试状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="状态")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    
    # 题目和答案
    questions = JSONField(verbose_name="题目列表", help_text="存储题目ID列表")
    answers = JSONField(default=dict, verbose_name="答案记录")
    
    # 成绩统计
    score = models.IntegerField(null=True, blank=True, verbose_name="得分")
    correct_count = models.IntegerField(default=0, verbose_name="正确题数")
    total_count = models.IntegerField(default=0, verbose_name="总题数")
    
    class Meta:
        db_table = "choice_exam_session"
        verbose_name = "考试会话"
        verbose_name_plural = "考试会话"
        ordering = ['-create_time']
        unique_together = ['paper', 'user']  # 每个用户每张试卷只能有一个会话
    
    def __str__(self):
        return f"{self.user.username} - {self.paper.title}"
    
    def start_exam(self):
        """
        开始考试
        """
        if self.status == 'created':
            self.status = 'started'
            self.start_time = timezone.now()
            self.save()
    
    def submit_exam(self):
        """
        提交考试
        """
        if self.status == 'started':
            self.status = 'submitted'
            self.submit_time = timezone.now()
            self.end_time = self.submit_time
            self.calculate_score()
            self.save()
    
    def timeout_exam(self):
        """
        考试超时
        """
        if self.status == 'started':
            self.status = 'timeout'
            self.end_time = timezone.now()
            self.calculate_score()
            self.save()
    
    def calculate_score(self):
        """
        计算考试成绩
        """
        if not self.questions:
            return
        
        question_ids = self.questions
        questions = ChoiceQuestion.objects.filter(id__in=question_ids)
        
        correct_count = 0
        total_count = len(questions)
        
        for question in questions:
            question_id = str(question.id)
            user_answer = self.answers.get(question_id)
            
            if user_answer and self.is_answer_correct(question, user_answer):
                correct_count += 1
        
        self.correct_count = correct_count
        self.total_count = total_count
        
        # 计算分数
        if total_count > 0:
            self.score = int((correct_count / total_count) * self.paper.total_score)
        else:
            self.score = 0
    
    def is_answer_correct(self, question, user_answer):
        """
        判断答案是否正确
        支持前端提交的索引格式和后端存储的字母格式
        """
        if user_answer is None:
            return False
            
        # 获取选项键值映射
        option_keys = []
        if question.options:
            if isinstance(question.options, str):
                import json
                options = json.loads(question.options)
            else:
                options = question.options
            
            if isinstance(options, list):
                option_keys = [opt.get('key', chr(65 + i)) for i, opt in enumerate(options)]
            
        if question.question_type == 'single':
            # 处理前端提交的索引格式 [0] -> 'A'
            if isinstance(user_answer, list) and len(user_answer) == 1:
                index = user_answer[0]
                if isinstance(index, int) and 0 <= index < len(option_keys):
                    user_answer = option_keys[index]
            # 处理直接提交的索引格式 0 -> 'A'
            elif isinstance(user_answer, int) and 0 <= user_answer < len(option_keys):
                user_answer = option_keys[user_answer]
                
            return user_answer == question.correct_answer
            
        elif question.question_type == 'multiple':
            # 处理多选题的索引格式
            if isinstance(user_answer, list):
                converted_answers = []
                for ans in user_answer:
                    if isinstance(ans, int) and 0 <= ans < len(option_keys):
                        converted_answers.append(option_keys[ans])
                    else:
                        converted_answers.append(ans)
                user_answer = converted_answers
                
            if isinstance(user_answer, list) and isinstance(question.correct_answer, list):
                return set(user_answer) == set(question.correct_answer)
                
        return False
    
    def get_remaining_time(self):
        """
        获取剩余时间（秒）
        """
        if not self.start_time or self.status != 'started':
            return 0
        
        elapsed = timezone.now() - self.start_time
        total_seconds = self.paper.duration * 60
        remaining = total_seconds - elapsed.total_seconds()
        
        return max(0, int(remaining))
    
    def is_timeout(self):
        """
        检查是否超时
        """
        return self.get_remaining_time() <= 0