# -*- coding: utf-8 -*-
"""
统一判题系统序列化器
用于API请求参数验证和响应数据序列化
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError


class UnifiedSubmissionSerializer(serializers.Serializer):
    """
    统一提交请求序列化器
    """
    question_type = serializers.ChoiceField(
        choices=['programming', 'choice'],
        required=True,
        help_text="题目类型：programming(编程题) 或 choice(选择题)"
    )
    
    question_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="题目ID"
    )
    
    # 编程题相关字段
    code = serializers.CharField(
        required=False,
        max_length=65536,
        help_text="代码内容（编程题必需）"
    )
    
    language = serializers.CharField(
        required=False,
        max_length=20,
        help_text="编程语言（编程题必需）"
    )
    
    # 选择题相关字段
    selected_answer = serializers.CharField(
        required=False,
        max_length=500,
        help_text="选择的答案（选择题必需）"
    )
    
    # 可选字段
    contest_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="竞赛ID（可选）"
    )
    
    captcha = serializers.CharField(
        required=False,
        max_length=10,
        help_text="验证码（可选）"
    )
    
    def validate(self, attrs):
        """
        交叉字段验证
        """
        question_type = attrs.get('question_type')
        
        if question_type == 'programming':
            # 编程题必须提供代码和语言
            if not attrs.get('code'):
                raise serializers.ValidationError("编程题必须提供代码")
            if not attrs.get('language'):
                raise serializers.ValidationError("编程题必须指定编程语言")
            
            # 验证编程语言
            valid_languages = [
                'C', 'C++', 'Java', 'Python2', 'Python3', 'JavaScript', 
                'Go', 'Rust', 'Kotlin', 'Swift', 'C#', 'PHP'
            ]
            if attrs.get('language') not in valid_languages:
                raise serializers.ValidationError(f"不支持的编程语言: {attrs.get('language')}")
                
        elif question_type == 'choice':
            # 选择题必须提供选择的答案
            if not attrs.get('selected_answer'):
                raise serializers.ValidationError("选择题必须提供选择的答案")
        
        return attrs


class SubmissionListSerializer(serializers.Serializer):
    """
    提交记录列表查询序列化器
    """
    user_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="用户ID"
    )
    
    question_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="题目ID"
    )
    
    question_type = serializers.ChoiceField(
        choices=['all', 'programming', 'choice'],
        default='all',
        help_text="题目类型筛选"
    )
    
    result = serializers.CharField(
        required=False,
        max_length=50,
        help_text="结果状态筛选"
    )
    
    page = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="页码"
    )
    
    page_size = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text="每页大小"
    )
    
    def validate(self, attrs):
        """
        验证查询参数组合
        """
        user_id = attrs.get('user_id')
        question_id = attrs.get('question_id')
        
        # user_id 和 question_id 不能同时为空（除非是管理员查询最近提交）
        if not user_id and not question_id:
            # 这种情况需要在API中进行权限检查
            pass
        
        return attrs


class UserStatisticsSerializer(serializers.Serializer):
    """
    用户统计信息查询序列化器
    """
    user_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="用户ID（可选，默认为当前用户）"
    )


class SubmissionDetailSerializer(serializers.Serializer):
    """
    提交详情查询序列化器
    """
    submission_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="提交ID"
    )
    
    question_type = serializers.ChoiceField(
        choices=['programming', 'choice'],
        required=True,
        help_text="题目类型"
    )


class JudgeStatusSerializer(serializers.Serializer):
    """
    判题状态查询序列化器
    """
    submission_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="提交ID"
    )
    
    question_type = serializers.ChoiceField(
        choices=['programming', 'choice'],
        required=True,
        help_text="题目类型"
    )


class QuestionMixSerializer(serializers.Serializer):
    """
    混合题目查询序列化器
    用于获取编程题和选择题的混合列表
    """
    question_types = serializers.MultipleChoiceField(
        choices=['programming', 'choice'],
        default=['programming', 'choice'],
        help_text="题目类型列表"
    )
    
    difficulty = serializers.CharField(
        required=False,
        max_length=20,
        help_text="难度筛选"
    )
    
    category_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="分类ID筛选"
    )
    
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="标签ID列表筛选"
    )
    
    keyword = serializers.CharField(
        required=False,
        max_length=100,
        help_text="关键词搜索"
    )
    
    is_public = serializers.BooleanField(
        default=True,
        help_text="是否只显示公开题目"
    )
    
    page = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="页码"
    )
    
    page_size = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text="每页大小"
    )
    
    order_by = serializers.ChoiceField(
        choices=['create_time', '-create_time', 'difficulty', '-difficulty', 
                'submission_number', '-submission_number', 'accepted_number', '-accepted_number'],
        default='-create_time',
        help_text="排序方式"
    )


class ContestSubmissionSerializer(serializers.Serializer):
    """
    竞赛提交序列化器
    """
    contest_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="竞赛ID"
    )
    
    question_type = serializers.ChoiceField(
        choices=['programming', 'choice'],
        required=True,
        help_text="题目类型"
    )
    
    question_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="题目ID"
    )
    
    # 编程题字段
    code = serializers.CharField(
        required=False,
        max_length=65536,
        help_text="代码内容"
    )
    
    language = serializers.CharField(
        required=False,
        max_length=20,
        help_text="编程语言"
    )
    
    # 选择题字段
    selected_answer = serializers.CharField(
        required=False,
        max_length=500,
        help_text="选择的答案"
    )
    
    def validate(self, attrs):
        """
        验证竞赛提交参数
        """
        question_type = attrs.get('question_type')
        
        if question_type == 'programming':
            if not attrs.get('code') or not attrs.get('language'):
                raise serializers.ValidationError("编程题必须提供代码和编程语言")
        elif question_type == 'choice':
            if not attrs.get('selected_answer'):
                raise serializers.ValidationError("选择题必须提供选择的答案")
        
        return attrs


class BatchJudgeSerializer(serializers.Serializer):
    """
    批量判题序列化器
    """
    submissions = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100,
        help_text="提交列表"
    )
    
    priority = serializers.ChoiceField(
        choices=['high', 'normal', 'low'],
        default='normal',
        help_text="判题优先级"
    )
    
    def validate_submissions(self, value):
        """
        验证提交列表格式
        """
        for i, submission in enumerate(value):
            if 'question_type' not in submission:
                raise serializers.ValidationError(f"第{i+1}个提交缺少question_type字段")
            
            if 'question_id' not in submission:
                raise serializers.ValidationError(f"第{i+1}个提交缺少question_id字段")
            
            question_type = submission.get('question_type')
            if question_type not in ['programming', 'choice']:
                raise serializers.ValidationError(f"第{i+1}个提交的question_type无效")
            
            if question_type == 'programming':
                if 'code' not in submission or 'language' not in submission:
                    raise serializers.ValidationError(f"第{i+1}个编程题提交缺少code或language字段")
            elif question_type == 'choice':
                if 'selected_answer' not in submission:
                    raise serializers.ValidationError(f"第{i+1}个选择题提交缺少selected_answer字段")
        
        return value


class RejudgeSerializer(serializers.Serializer):
    """
    重新判题序列化器
    """
    submission_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=1000,
        help_text="提交ID列表"
    )
    
    question_type = serializers.ChoiceField(
        choices=['programming', 'choice'],
        required=True,
        help_text="题目类型"
    )
    
    reason = serializers.CharField(
        required=False,
        max_length=200,
        help_text="重新判题原因"
    )