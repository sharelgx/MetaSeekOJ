#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择题集成测试脚本
测试选择题功能是否正常集成到OnlineJudge系统中
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.contrib.auth import get_user_model
from choice_question.models import ChoiceQuestion, Category, QuestionTag
from choice_question.utils.judge import ChoiceQuestionJudge

User = get_user_model()

class ChoiceQuestionIntegrationTest:
    """
    选择题集成测试类
    """
    
    def __init__(self):
        self.base_url = 'http://localhost:8000'
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✓ PASS" if success else "✗ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message,
            'timestamp': timestamp
        })
    
    def test_models_import(self):
        """测试模型导入"""
        try:
            from choice_question.models import ChoiceQuestion, Category, QuestionTag, ChoiceQuestionSubmission, WrongQuestion
            self.log_test("模型导入测试", True, "所有模型成功导入")
            return True
        except ImportError as e:
            self.log_test("模型导入测试", False, f"导入失败: {e}")
            return False
    
    def test_database_tables(self):
        """测试数据库表是否存在"""
        try:
            # 测试是否能查询各个表
            ChoiceQuestion.objects.count()
            Category.objects.count()
            QuestionTag.objects.count()
            self.log_test("数据库表测试", True, "所有表都可以正常访问")
            return True
        except Exception as e:
            self.log_test("数据库表测试", False, f"数据库访问失败: {e}")
            return False
    
    def test_create_test_data(self):
        """创建测试数据"""
        try:
            # 创建测试分类
            category, created = Category.objects.get_or_create(
                name="测试分类",
                defaults={'description': '用于集成测试的分类'}
            )
            
            # 创建测试标签
            tag, created = QuestionTag.objects.get_or_create(
                name="测试标签",
                defaults={'description': '用于集成测试的标签'}
            )
            
            # 创建测试用户
            user, created = User.objects.get_or_create(
                username="test_user",
                defaults={
                    'email': 'test@example.com'
                }
            )
            
            # 创建用户资料
            from account.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'real_name': '测试用户'
                }
            )
            
            # 创建测试选择题
            question, created = ChoiceQuestion.objects.get_or_create(
                _id="TEST001",
                defaults={
                    'title': '测试选择题',
                    'description': '这是一道用于集成测试的选择题',
                    'question_type': 'single',
                    'options': ['选项A', '选项B', '选项C', '选项D'],
                    'correct_answer': 'A',
                    'explanation': '正确答案是A',
                    'difficulty': 'easy',
                    'score': 10,
                    'category': category,
                    'created_by': user,
                    'is_public': True,
                    'visible': True
                }
            )
            
            # 添加标签
            question.tags.add(tag)
            
            self.log_test("测试数据创建", True, f"创建了测试题目: {question.title}")
            return question, user
        except Exception as e:
            self.log_test("测试数据创建", False, f"创建失败: {e}")
            return None, None
    
    def test_judge_functionality(self, question, user):
        """测试判题功能"""
        try:
            judge = ChoiceQuestionJudge()
            
            # 测试正确答案
            result = judge.judge_submission(question, 'A', user, save_submission=False)
            if result['is_correct'] and result['score'] == 10:
                self.log_test("判题功能测试(正确答案)", True, f"得分: {result['score']}/10")
            else:
                self.log_test("判题功能测试(正确答案)", False, f"期望正确但得到: {result}")
                return False
            
            # 测试错误答案
            result = judge.judge_submission(question, 'B', user, save_submission=False)
            if not result['is_correct'] and result['score'] == 0:
                self.log_test("判题功能测试(错误答案)", True, f"得分: {result['score']}/10")
            else:
                self.log_test("判题功能测试(错误答案)", False, f"期望错误但得到: {result}")
                return False
            
            return True
        except Exception as e:
            self.log_test("判题功能测试", False, f"测试失败: {e}")
            return False
    
    def test_api_endpoints(self):
        """测试API端点"""
        try:
            # 测试选择题列表API
            response = requests.get(f"{self.base_url}/api/plugin/choice/questions/", timeout=5)
            if response.status_code == 200:
                self.log_test("API端点测试(题目列表)", True, f"状态码: {response.status_code}")
            else:
                self.log_test("API端点测试(题目列表)", False, f"状态码: {response.status_code}")
                return False
            
            # 测试分类列表API
            response = requests.get(f"{self.base_url}/api/plugin/choice/categories/", timeout=5)
            if response.status_code == 200:
                self.log_test("API端点测试(分类列表)", True, f"状态码: {response.status_code}")
            else:
                self.log_test("API端点测试(分类列表)", False, f"状态码: {response.status_code}")
                return False
            
            return True
        except requests.exceptions.RequestException as e:
            self.log_test("API端点测试", False, f"请求失败: {e}")
            return False
    
    def test_unified_judge_system(self):
        """测试统一判题系统"""
        try:
            from judge.unified_dispatcher import unified_dispatcher, QuestionTypeDetector
            
            # 测试题目类型检测
            question_type = QuestionTypeDetector.detect_question_type("1", "choice")
            if question_type == "choice":
                self.log_test("统一判题系统(类型检测)", True, f"检测到类型: {question_type}")
            else:
                self.log_test("统一判题系统(类型检测)", False, f"期望choice但得到: {question_type}")
                return False
            
            self.log_test("统一判题系统", True, "统一判题系统组件正常")
            return True
        except Exception as e:
            self.log_test("统一判题系统", False, f"测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("选择题集成测试开始")
        print("="*60)
        
        # 运行各项测试
        tests_passed = 0
        total_tests = 0
        
        # 基础测试
        if self.test_models_import():
            tests_passed += 1
        total_tests += 1
        
        if self.test_database_tables():
            tests_passed += 1
        total_tests += 1
        
        # 创建测试数据
        question, user = self.test_create_test_data()
        if question and user:
            tests_passed += 1
        total_tests += 1
        
        # 功能测试
        if question and user:
            if self.test_judge_functionality(question, user):
                tests_passed += 2  # 正确和错误答案各一个测试
            total_tests += 2
        
        if self.test_api_endpoints():
            tests_passed += 2  # 两个API端点
        total_tests += 2
        
        if self.test_unified_judge_system():
            tests_passed += 1
        total_tests += 1
        
        # 输出测试结果
        print("\n" + "="*60)
        print(f"测试完成: {tests_passed}/{total_tests} 通过")
        print("="*60)
        
        if tests_passed == total_tests:
            print("🎉 所有测试通过！选择题功能已成功集成到OnlineJudge系统中。")
            return True
        else:
            print(f"⚠️  有 {total_tests - tests_passed} 个测试失败，请检查相关功能。")
            return False

if __name__ == "__main__":
    tester = ChoiceQuestionIntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)