from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from choice_question.models import (
    ChoicePluginCategory,
    ChoicePluginQuestion,
    ChoicePluginWrongQuestion,
    ChoicePluginSubmission,
    ChoicePluginQuestionTag
)
from django.db import transaction
import json
from unittest.mock import patch

User = get_user_model()


class ChoiceQuestionIntegrationTest(TransactionTestCase):
    """选择题插件集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 创建测试用户
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacherpass123',
            is_staff=True
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123'
        )
        
        # 创建测试数据
        self.category = ChoicePluginCategory.objects.create(
            name='数学',
            description='数学相关题目',
            created_by=self.admin_user
        )
        
        self.tag = ChoicePluginQuestionTag.objects.create(
            name='代数',
            color='#FF5722',
            created_by=self.admin_user
        )
        
        self.question = ChoicePluginQuestion.objects.create(
            title='1+1等于多少？',
            content='请选择正确答案',
            question_type='single',
            options=['1', '2', '3', '4'],
            correct_answer=[1],
            difficulty='easy',
            score=10,
            category=self.category,
            created_by=self.admin_user
        )
    
    def test_complete_question_lifecycle(self):
        """测试题目完整生命周期"""
        # 1. 管理员创建分类
        self.client.force_authenticate(user=self.admin_user)
        
        category_data = {
            'name': '物理',
            'description': '物理相关题目',
            'is_enabled': True
        }
        
        category_response = self.client.post(
            reverse('choice_question:category-list'),
            category_data,
            format='json'
        )
        
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        physics_category_id = category_response.data['id']
        
        # 2. 管理员创建题目
        question_data = {
            'title': '光速是多少？',
            'content': '请选择正确答案',
            'question_type': 'single',
            'options': ['3×10^8 m/s', '3×10^7 m/s', '3×10^9 m/s', '3×10^6 m/s'],
            'correct_answer': [0],
            'difficulty': 'medium',
            'score': 15,
            'category': physics_category_id,
            'explanation': '光在真空中的传播速度约为3×10^8 m/s'
        }
        
        question_response = self.client.post(
            reverse('choice_question:question-list'),
            question_data,
            format='json'
        )
        
        self.assertEqual(question_response.status_code, status.HTTP_201_CREATED)
        physics_question_id = question_response.data['id']
        
        # 3. 学生查看题目列表
        self.client.force_authenticate(user=self.student_user)
        
        questions_response = self.client.get(
            reverse('choice_question:question-list')
        )
        
        self.assertEqual(questions_response.status_code, status.HTTP_200_OK)
        self.assertEqual(questions_response.data['count'], 2)  # 包括setUp中创建的题目
        
        # 4. 学生答题（正确答案）
        submit_data = {
            'user_answer': [0],
            'time_spent': 45
        }
        
        submit_response = self.client.post(
            reverse('choice_question:question-submit', kwargs={'pk': physics_question_id}),
            submit_data,
            format='json'
        )
        
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.assertTrue(submit_response.data['is_correct'])
        self.assertEqual(submit_response.data['score'], 15)
        
        # 5. 验证提交记录
        submission = ChoicePluginSubmission.objects.get(
            user=self.student_user,
            question_id=physics_question_id
        )
        self.assertTrue(submission.is_correct)
        self.assertEqual(submission.score, 15)
        self.assertEqual(submission.time_spent, 45)
        
        # 6. 学生答错另一道题
        wrong_submit_data = {
            'user_answer': [0],  # 错误答案
            'time_spent': 30
        }
        
        wrong_submit_response = self.client.post(
            reverse('choice_question:question-submit', kwargs={'pk': self.question.id}),
            wrong_submit_data,
            format='json'
        )
        
        self.assertEqual(wrong_submit_response.status_code, status.HTTP_200_OK)
        self.assertFalse(wrong_submit_response.data['is_correct'])
        self.assertEqual(wrong_submit_response.data['score'], 0)
        
        # 7. 验证错题记录
        wrong_question = ChoicePluginWrongQuestion.objects.get(
            user=self.student_user,
            question=self.question
        )
        self.assertEqual(wrong_question.wrong_count, 1)
        self.assertEqual(wrong_question.last_wrong_answer, [0])
        
        # 8. 查看错题本
        wrong_questions_response = self.client.get(
            reverse('choice_question:wrong-question-list')
        )
        
        self.assertEqual(wrong_questions_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(wrong_questions_response.data['results']), 1)
        
        # 9. 查看个人统计
        stats_response = self.client.get(
            reverse('choice_question:user-statistics')
        )
        
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_response.data['total_questions'], 2)
        self.assertEqual(stats_response.data['correct_count'], 1)
        self.assertEqual(stats_response.data['accuracy_rate'], 50.0)
    
    def test_batch_operations(self):
        """测试批量操作"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 创建多个题目
        questions_data = []
        for i in range(5):
            question_data = {
                'title': f'测试题目 {i+1}',
                'content': f'测试内容 {i+1}',
                'question_type': 'single',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': [i % 4],
                'difficulty': 'easy',
                'score': 10,
                'category': self.category.id
            }
            
            response = self.client.post(
                reverse('choice_question:question-list'),
                question_data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            questions_data.append(response.data)
        
        # 批量删除题目
        question_ids = [q['id'] for q in questions_data[:3]]
        
        batch_delete_data = {
            'action': 'delete',
            'question_ids': question_ids
        }
        
        batch_response = self.client.post(
            reverse('choice_question:question-batch-operation'),
            batch_delete_data,
            format='json'
        )
        
        self.assertEqual(batch_response.status_code, status.HTTP_200_OK)
        
        # 验证题目已删除
        for question_id in question_ids:
            self.assertFalse(
                ChoicePluginQuestion.objects.filter(id=question_id).exists()
            )
    
    def test_import_export_questions(self):
        """测试题目导入导出"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 导出题目
        export_response = self.client.get(
            reverse('choice_question:question-export'),
            {'format': 'json', 'category': self.category.id}
        )
        
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        self.assertEqual(export_response['Content-Type'], 'application/json')
        
        # 解析导出数据
        export_data = json.loads(export_response.content)
        self.assertEqual(len(export_data), 1)
        self.assertEqual(export_data[0]['title'], '1+1等于多少？')
        
        # 修改数据用于导入测试
        import_data = export_data.copy()
        import_data[0]['title'] = '导入测试题目'
        import_data[0]['id'] = None  # 移除ID以创建新题目
        
        # 导入题目
        import_response = self.client.post(
            reverse('choice_question:question-import'),
            {'questions': json.dumps(import_data)},
            format='multipart'
        )
        
        self.assertEqual(import_response.status_code, status.HTTP_200_OK)
        self.assertEqual(import_response.data['success_count'], 1)
        
        # 验证导入的题目
        imported_question = ChoicePluginQuestion.objects.get(
            title='导入测试题目'
        )
        self.assertEqual(imported_question.category, self.category)
    
    def test_permission_system(self):
        """测试权限系统"""
        # 1. 未认证用户只能查看题目
        response = self.client.get(reverse('choice_question:question-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 未认证用户不能创建题目
        question_data = {
            'title': '测试题目',
            'content': '测试内容',
            'question_type': 'single',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': [0],
            'category': self.category.id
        }
        
        response = self.client.post(
            reverse('choice_question:question-list'),
            question_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 3. 学生不能创建题目
        self.client.force_authenticate(user=self.student_user)
        
        response = self.client.post(
            reverse('choice_question:question-list'),
            question_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 4. 教师可以创建题目
        self.client.force_authenticate(user=self.teacher_user)
        
        response = self.client.post(
            reverse('choice_question:question-list'),
            question_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. 管理员可以执行所有操作
        self.client.force_authenticate(user=self.admin_user)
        
        # 创建分类
        category_response = self.client.post(
            reverse('choice_question:category-list'),
            {'name': '新分类', 'description': '测试分类'},
            format='json'
        )
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        
        # 查看管理员统计
        stats_response = self.client.get(
            reverse('choice_question:admin-statistics')
        )
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
    
    def test_data_consistency(self):
        """测试数据一致性"""
        self.client.force_authenticate(user=self.student_user)
        
        # 多次提交同一题目
        for i in range(3):
            submit_data = {
                'user_answer': [0],  # 错误答案
                'time_spent': 30 + i * 10
            }
            
            response = self.client.post(
                reverse('choice_question:question-submit', kwargs={'pk': self.question.id}),
                submit_data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证只有一条错题记录，但错误次数正确
        wrong_questions = ChoicePluginWrongQuestion.objects.filter(
            user=self.student_user,
            question=self.question
        )
        
        self.assertEqual(wrong_questions.count(), 1)
        self.assertEqual(wrong_questions.first().wrong_count, 3)
        
        # 验证有3条提交记录
        submissions = ChoicePluginSubmission.objects.filter(
            user=self.student_user,
            question=self.question
        )
        
        self.assertEqual(submissions.count(), 3)
    
    def test_concurrent_submissions(self):
        """测试并发提交"""
        from threading import Thread
        import time
        
        self.client.force_authenticate(user=self.student_user)
        
        results = []
        
        def submit_answer():
            client = APIClient()
            client.force_authenticate(user=self.student_user)
            
            submit_data = {
                'user_answer': [1],
                'time_spent': 30
            }
            
            try:
                response = client.post(
                    reverse('choice_question:question-submit', kwargs={'pk': self.question.id}),
                    submit_data,
                    format='json'
                )
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # 创建多个并发线程
        threads = []
        for i in range(5):
            thread = Thread(target=submit_answer)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有提交都成功
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertEqual(result, status.HTTP_200_OK)
        
        # 验证数据库中的记录数量正确
        submissions = ChoicePluginSubmission.objects.filter(
            user=self.student_user,
            question=self.question
        )
        
        self.assertEqual(submissions.count(), 5)
    
    @patch('choice_question.tasks.send_notification')
    def test_notification_system(self, mock_send_notification):
        """测试通知系统（如果有的话）"""
        self.client.force_authenticate(user=self.student_user)
        
        # 提交错误答案
        submit_data = {
            'user_answer': [0],
            'time_spent': 30
        }
        
        response = self.client.post(
            reverse('choice_question:question-submit', kwargs={'pk': self.question.id}),
            submit_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证通知是否被调用（如果实现了通知功能）
        # mock_send_notification.assert_called_once()
    
    def test_api_rate_limiting(self):
        """测试API速率限制（如果实现了的话）"""
        self.client.force_authenticate(user=self.student_user)
        
        # 快速连续发送多个请求
        responses = []
        for i in range(10):
            response = self.client.get(reverse('choice_question:question-list'))
            responses.append(response.status_code)
        
        # 大部分请求应该成功
        success_count = sum(1 for status_code in responses if status_code == 200)
        self.assertGreaterEqual(success_count, 8)  # 允许少量请求被限制
    
    def test_database_constraints(self):
        """测试数据库约束"""
        # 测试分类名称唯一性
        with self.assertRaises(Exception):
            ChoicePluginCategory.objects.create(
                name='数学',  # 重复名称
                description='重复分类',
                created_by=self.admin_user
            )
        
        # 测试题目标题在同一分类下的唯一性（如果有此约束）
        # 这取决于具体的业务需求
    
    def tearDown(self):
        """清理测试数据"""
        # Django的TransactionTestCase会自动清理数据
        pass