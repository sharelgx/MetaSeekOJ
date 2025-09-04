#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试考试模式修复
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.contrib.auth.models import User
from choice_question.models import ExamPaper, Category, ChoiceQuestion
from choice_question.api.exam import ExamPaperAPI
from django.test import RequestFactory
from django.contrib.auth import get_user_model
import json

def test_exam_paper_creation():
    """
    测试考试试卷创建功能
    """
    print("=== 测试考试试卷创建功能 ===")
    
    try:
        # 获取或创建测试用户
        User = get_user_model()
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_active': True
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
            print(f"创建测试用户: {test_user.username}")
        else:
            print(f"使用现有测试用户: {test_user.username}")
        
        # 获取分类信息
        categories = Category.objects.filter(is_active=True)[:2]
        if not categories.exists():
            print("警告: 没有找到可用的分类")
            return False
        
        category_ids = [cat.id for cat in categories]
        print(f"使用分类: {[cat.name for cat in categories]}")
        
        # 检查每个分类下的题目数量（包括子分类）
        for category in categories:
            descendant_categories = category.get_descendants(include_self=True)
            question_count = ChoiceQuestion.objects.filter(
                category__in=descendant_categories,
                is_public=True
            ).count()
            print(f"分类 '{category.name}' (包含子分类) 下有 {question_count} 道题目")
        
        # 创建请求工厂
        factory = RequestFactory()
        
        # 准备测试数据
        exam_data = {
            'title': '测试考试试卷',
            'description': '基于当前筛选条件的考试',
            'duration': 30,  # 30分钟
            'question_count': 5,  # 5题
            'total_score': 100,  # 总分100分
            'categories': category_ids,
            'difficulty_distribution': {
                'easy': 2,
                'medium': 2,
                'hard': 1
            }
        }
        
        print(f"测试数据: {json.dumps(exam_data, indent=2, ensure_ascii=False)}")
        
        # 创建POST请求
        request = factory.post(
            '/api/choice_question/exam-papers/',
            data=exam_data,  # 直接传递字典，不需要JSON序列化
            content_type='application/json'
        )
        request.user = test_user
        # 为WSGIRequest添加data属性（模拟DRF的Request对象）
        request.data = exam_data
        
        # 调用API
        api = ExamPaperAPI()
        response = api.post(request)
        
        print(f"API响应状态: {response.status_code}")
        print(f"API响应内容: {response.data}")
        
        if response.status_code == 200 and response.data.get('error') is None:
            paper_data = response.data.get('data')
            if paper_data:
                paper_id = paper_data.get('id')
                print(f"✅ 试卷创建成功! ID: {paper_id}")
                
                # 测试题目生成
                paper = ExamPaper.objects.get(id=paper_id)
                questions = paper.generate_questions()
                print(f"✅ 生成题目数量: {len(questions)}")
                
                # 显示题目详情
                for i, question in enumerate(questions, 1):
                    print(f"  {i}. [{question.category.name}] {question.title[:50]}...")
                
                return True
            else:
                print(f"❌ 试卷创建失败: 响应中没有试卷数据")
                return False
        else:
            print(f"❌ 试卷创建失败: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """
    清理测试数据
    """
    print("\n=== 清理测试数据 ===")
    try:
        # 删除测试试卷
        deleted_count = ExamPaper.objects.filter(title__contains='测试考试试卷').delete()[0]
        print(f"删除了 {deleted_count} 个测试试卷")
        
        # 删除测试用户（可选）
        # User.objects.filter(username='testuser').delete()
        
    except Exception as e:
        print(f"清理数据时出错: {e}")

if __name__ == '__main__':
    success = test_exam_paper_creation()
    
    if success:
        print("\n🎉 考试模式修复测试通过!")
    else:
        print("\n❌ 考试模式修复测试失败!")
    
    # 清理测试数据
    cleanup_test_data()