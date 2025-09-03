#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试试卷API的脚本
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
sys.path.append('/home/metaspeekoj/OnlineJudge')
django.setup()

from account.models import User, AdminType
from choice_question.models import ExamPaper, ExamSession, ChoiceQuestion, Category
from choice_question.api.exam import ExamPaperAPI, ExamSessionAPI
from django.test import RequestFactory
from django.http import JsonResponse

def create_test_exam_paper():
    """创建测试试卷"""
    try:
        # 创建或获取管理员用户
        try:
            admin_user = User.objects.get(username='admin')
            print(f"管理员用户已存在: {admin_user.username}")
        except User.DoesNotExist:
            admin_user = User.objects.create(
                username='admin',
                email='admin@example.com',
                admin_type=AdminType.SUPER_ADMIN
            )
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"创建管理员用户: {admin_user.username}")
        
        # 检查是否有选择题
        question_count = ChoiceQuestion.objects.filter(is_public=True).count()
        print(f"当前可用选择题数量: {question_count}")
        
        if question_count == 0:
            print("警告: 没有可用的选择题，需要先创建一些选择题")
            return None
        
        # 创建测试试卷
        exam_paper = ExamPaper.objects.create(
            title="测试试卷",
            description="这是一个用于测试的试卷",
            duration=30,  # 30分钟
            question_count=min(10, question_count),  # 最多10题
            total_score=100,
            difficulty_distribution={
                'easy': min(5, question_count),
                'medium': min(3, question_count - 5) if question_count > 5 else 0,
                'hard': min(2, question_count - 8) if question_count > 8 else 0
            },
            created_by=admin_user
        )
        
        print(f"创建测试试卷成功: {exam_paper.title} (ID: {exam_paper.id})")
        print(f"试卷配置: 时长{exam_paper.duration}分钟, {exam_paper.question_count}题, 总分{exam_paper.total_score}")
        
        # 测试生成题目
        questions = exam_paper.generate_questions()
        print(f"生成题目数量: {len(questions)}")
        
        for i, q in enumerate(questions[:3], 1):
            print(f"  {i}. {q.description[:50]}... (难度: {q.difficulty})")
        
        return exam_paper
        
    except Exception as e:
        print(f"创建测试试卷失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_user():
    """创建测试用户"""
    try:
        user = User.objects.get(username='test_user')
        print(f"用户已存在: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create(
            username='test_user',
            email='test@example.com',
            admin_type=AdminType.SUPER_ADMIN
        )
        user.set_password('testpass123')
        user.save()
        print(f"创建用户: {user.username}")
    return user

def test_exam_session():
    """
    测试考试会话
    """
    try:
        # 获取测试试卷
        exam_paper = ExamPaper.objects.filter(title="测试试卷").first()
        if not exam_paper:
            print("未找到测试试卷，先创建试卷")
            exam_paper = create_test_exam_paper()
            if not exam_paper:
                return
        
        # 获取测试用户
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com'
            }
        )
        
        if created:
            test_user.set_password('test123')
            test_user.save()
            print(f"创建测试用户: {test_user.username}")
        
        # 创建考试会话
        session, created = ExamSession.objects.get_or_create(
            paper=exam_paper,
            user=test_user,
            defaults={
                'questions': [q.id for q in exam_paper.generate_questions()],
                'total_count': exam_paper.question_count
            }
        )
        
        if created:
            print(f"创建考试会话成功: {session.id}")
        else:
            print(f"使用现有考试会话: {session.id}")
        
        print(f"会话状态: {session.status}")
        print(f"题目数量: {len(session.questions) if session.questions else 0}")
        
        return session
        
    except Exception as e:
        print(f"测试考试会话失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("=== 测试试卷API ===")
    
    # 创建测试试卷
    paper = create_test_exam_paper()
    
    if paper:
        print("\n=== 测试考试会话 ===")
        session = test_exam_session()
        
        if session:
            print("\n=== 测试完成 ===")
            print(f"试卷ID: {paper.id}")
            print(f"会话ID: {session.id}")
            print("\n可以使用以下URL测试API:")
            print(f"- 试卷列表: http://localhost:8000/api/plugin/choice/exam-papers/")
            print(f"- 试卷详情: http://localhost:8000/api/plugin/choice/exam-papers/{paper.id}/")
            print(f"- 创建会话: http://localhost:8000/api/plugin/choice/exam-sessions/create/")
            print(f"- 会话详情: http://localhost:8000/api/plugin/choice/exam-sessions/{session.id}/")
    else:
        print("测试失败")