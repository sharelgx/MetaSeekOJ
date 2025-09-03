from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from choice_question.models import (
    Category,
    ChoiceQuestion,
    WrongQuestion,
    ChoiceQuestionSubmission,
    QuestionTag
)
import json

User = get_user_model()


class CategoryAPITest(TestCase):
    """分类API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com'
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        self.admin_user = User.objects.create(
            username='admin',
            email='admin@example.com',
            admin_type='Super Admin'
        )
        self.admin_user.set_password('adminpass123')
        self.admin_user.save()
        
        self.category = Category.objects.create(
            name='数学',
            description='数学相关题目'
        )
    
    def test_get_categories_list(self):
        """测试获取分类列表"""
        url = reverse('choice_question:category-list')
        response = self.client.get(url)
        
        print(f"Get categories response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查返回的数据结构
        if 'data' in response.data and 'results' in response.data['data']:
            self.assertEqual(len(response.data['data']['results']), 1)
            self.assertEqual(response.data['data']['results'][0]['name'], '数学')
        elif 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['name'], '数学')
        else:
            # 如果没有分页，直接检查数据
            self.assertEqual(len(response.data['data']), 1)
            self.assertEqual(response.data['data'][0]['name'], '数学')
    
    def test_create_category_as_admin(self):
        """测试管理员创建分类"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:category-list')
        data = {
            'name': '物理',
            'description': '物理相关题目',
            'is_enabled': True
        }
        
        response = self.client.post(url, data, format='json')
        
        print(f"Create category response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 检查返回的数据结构
        if 'data' in response.data:
            self.assertEqual(response.data['data']['name'], '物理')
        else:
            self.assertEqual(response.data['name'], '物理')
    
    def test_create_category_as_regular_user(self):
        """测试普通用户创建分类（应该失败）"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:category-list')
        data = {
            'name': '化学',
            'description': '化学相关题目'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_category(self):
        """测试更新分类"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:category-detail', kwargs={'pk': self.category.id})
        data = {
            'name': '高等数学',
            'description': '高等数学相关题目'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '高等数学')
    
    def test_delete_category(self):
        """测试删除分类"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:category-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())


class QuestionAPITest(TestCase):
    """题目API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.category = Category.objects.create(
            name='数学'
        )
        
        self.question = ChoiceQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',
            difficulty='easy',
            score=10,
            category=self.category,
            created_by=self.admin_user
        )
    
    def test_get_questions_list(self):
        """测试获取题目列表"""
        url = reverse('choice_question:question-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查返回格式
        if 'results' in response.data:
            # 如果是分页格式
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['title'], '1+1等于多少？')
        else:
            # 如果不是分页格式，直接检查数据
            self.assertEqual(len(response.data['data']['results']), 1)
            self.assertEqual(response.data['data']['results'][0]['title'], '1+1等于多少？')
    
    def test_get_question_detail(self):
        """测试获取题目详情"""
        url = reverse('choice_question:question-detail', kwargs={'pk': self.question.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查返回格式
        if 'data' in response.data:
            # 如果使用了success包装
            self.assertEqual(response.data['data']['title'], '1+1等于多少？')
            self.assertEqual(response.data['data']['options'], ['1', '2', '3', '4'])
        else:
            # 如果直接返回数据
            self.assertEqual(response.data['title'], '1+1等于多少？')
            # 检查选项格式（现在是包含key和text的对象数组）
        expected_options = [
            {'key': 'A', 'text': '1'},
            {'key': 'B', 'text': '2'},
            {'key': 'C', 'text': '3'},
            {'key': 'D', 'text': '4'}
        ]
        self.assertEqual(response.data['options'], expected_options)
    
    def test_create_question_as_admin(self):
        """测试管理员创建题目"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:question-list')
        data = {
            'title': '2+2等于多少？',
            'content': '请选择正确答案',
            'description': '这是一道简单的数学题',
            'question_type': 'single',
            'options': [
                {'key': 'A', 'value': '2'},
                {'key': 'B', 'value': '3'},
                {'key': 'C', 'value': '4'},
                {'key': 'D', 'value': '5'}
            ],
            'correct_answer': 'C',
            'difficulty': 'easy',
            'score': 10,
            'category': self.category.id
        }
        
        response = self.client.post(url, data, format='json')
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")
        else:
            print(f"Success response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 检查返回的数据结构
        if 'data' in response.data:
            self.assertEqual(response.data['data']['title'], '2+2等于多少？')
        else:
            self.assertEqual(response.data['title'], '2+2等于多少？')
    
    def test_create_question_as_regular_user(self):
        """测试普通用户创建题目（应该失败）"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:question-list')
        data = {
            'title': '3+3等于多少？',
            'content': '请选择正确答案',
            'description': '这是另一道简单的数学题',
            'question_type': 'single',
            'options': [
                {'key': 'A', 'value': '4'},
                {'key': 'B', 'value': '5'},
                {'key': 'C', 'value': '6'},
                {'key': 'D', 'value': '7'}
            ],
            'correct_answer': 'C',
            'category': self.category.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_filter_questions_by_category(self):
        """测试按分类筛选题目"""
        # 创建另一个分类和题目
        physics_category = Category.objects.create(
            name='物理'
        )
        
        ChoiceQuestion.objects.create(
            title='光速是多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '3×10^8 m/s'}, {'key': 'B', 'text': '3×10^7 m/s'}, {'key': 'C', 'text': '3×10^9 m/s'}, {'key': 'D', 'text': '3×10^6 m/s'}],
            correct_answer='A',
            difficulty='medium',
            score=15,
            category=physics_category,
            created_by=self.admin_user
        )
        
        url = reverse('choice_question:question-list')
        response = self.client.get(url, {'category': self.category.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], self.category.id)
    
    def test_filter_questions_by_difficulty(self):
        """测试按难度筛选题目"""
        # 创建不同难度的题目
        ChoiceQuestion.objects.create(
            title='复杂数学题',
            description='这是一道困难题',
            question_type='multiple',
            options=[{'key': 'A', 'text': 'A'}, {'key': 'B', 'text': 'B'}, {'key': 'C', 'text': 'C'}, {'key': 'D', 'text': 'D'}],
            correct_answer='A,C',
            difficulty='hard',
            score=30,
            category=self.category,
            created_by=self.admin_user
        )
        
        url = reverse('choice_question:question-list')
        response = self.client.get(url, {'difficulty': 'easy'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['difficulty'], 'easy')


class SubmissionAPITest(TestCase):
    """提交记录API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com'
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        self.admin_user = User.objects.create(
            username='admin',
            email='admin@example.com',
            admin_type='Admin'
        )
        self.admin_user.set_password('adminpass123')
        self.admin_user.save()
        
        self.category = Category.objects.create(
             name='数学'
         )
        
        self.question = ChoiceQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',
            difficulty='easy',
            score=10,
            category=self.category,
            created_by=self.admin_user
        )
    
    def test_submit_correct_answer(self):
        """测试提交正确答案"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:submission-list')
        data = {
            'question': self.question.id,
            'selected_answer': 'B',
            'time_spent': 30
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 直接从response.data获取数据
        self.assertTrue(response.data.get('is_correct', False))
        self.assertEqual(response.data.get('score', 0), 10)
        
        # 检查数据库中的提交记录
        submission = ChoiceQuestionSubmission.objects.get(
            user=self.user,
            question=self.question
        )
        self.assertTrue(submission.is_correct)
        self.assertEqual(submission.score, 10)
    
    def test_submit_incorrect_answer(self):
        """测试提交错误答案"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:submission-list')
        data = {
            'question': self.question.id,
            'selected_answer': 'A',
            'time_spent': 25
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 直接从response.data获取数据
        self.assertFalse(response.data.get('is_correct', True))
        self.assertEqual(response.data.get('score', -1), 0)
        
        # 检查是否创建了错题记录
        wrong_question = WrongQuestion.objects.get(
            user=self.user,
            question=self.question
        )
        self.assertEqual(wrong_question.wrong_count, 1)
        self.assertEqual(wrong_question.last_wrong_answer, 'A')
    
    def test_submit_without_authentication(self):
        """测试未认证用户提交答案（应该失败）"""
        url = reverse('choice_question:submission-list')
        data = {
            'question': self.question.id,
            'selected_answer': 'A',
            'time_spent': 20
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_submissions(self):
        """测试获取用户提交记录"""
        self.client.force_authenticate(user=self.user)
        
        # 先创建一些提交记录
        ChoiceQuestionSubmission.objects.create(
            user=self.user,
            question=self.question,
            selected_answer='B',
            is_correct=True,
            score=10,
            time_spent=30
        )
        
        url = reverse('choice_question:submission-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['id'], self.user.id)


class WrongQuestionAPITest(TestCase):
    """错题本API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com'
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        self.admin_user = User.objects.create(
            username='admin',
            email='admin@example.com',
            admin_type='Admin'
        )
        self.admin_user.set_password('adminpass123')
        self.admin_user.save()
        
        self.category = Category.objects.create(
             name='数学'
         )
        
        self.question = ChoiceQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',
            difficulty='easy',
            score=10,
            category=self.category,
            created_by=self.admin_user
        )
        
        self.wrong_question = WrongQuestion.objects.create(
            user=self.user,
            question=self.question,
            wrong_count=2,
            last_wrong_answer='A'
        )
    
    def test_get_wrong_questions(self):
        """测试获取错题列表"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:wrong-question-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查分页格式
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['question']['id'], self.question.id)
        else:
            # 如果不是分页格式，直接检查数据
            self.assertEqual(len(response.data['data']['results']), 1)
            self.assertEqual(response.data['data']['results'][0]['question']['id'], self.question.id)
    
    def test_resolve_wrong_question(self):
        """测试解决错题"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:wrong-question-resolve', kwargs={'pk': self.wrong_question.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 检查错题是否被标记为已掌握
        self.wrong_question.refresh_from_db()
        self.assertTrue(self.wrong_question.is_mastered)
    
    def test_remove_from_wrong_book(self):
        """测试从错题本中移除题目"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:wrong-question-detail', kwargs={'pk': self.wrong_question.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WrongQuestion.objects.filter(id=self.wrong_question.id).exists())


class TagAPITest(TestCase):
    """标签API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            username='admin',
            email='admin@example.com',
            admin_type='Super Admin'
        )
        self.admin_user.set_password('adminpass123')
        self.admin_user.save()
        
        self.tag = QuestionTag.objects.create(
            name='代数',
            color='#FF5722'
        )
    
    def test_get_tags_list(self):
        """测试获取标签列表"""
        url = reverse('choice_question:tag-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查返回格式（标准DRF分页格式）
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], '代数')
    
    def test_create_tag_as_admin(self):
        """测试管理员创建标签"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:tag-list')
        data = {
            'name': '几何',
            'color': '#2196F3',
            'description': '几何相关题目标签'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 检查返回数据格式（直接返回创建的对象）
        self.assertEqual(response.data['name'], '几何')
        self.assertEqual(response.data['color'], '#2196F3')


class StatisticsAPITest(TestCase):
    """统计API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.category = Category.objects.create(
            name='数学'
        )
        
        self.question = ChoiceQuestion.objects.create(
            title='测试题目',
            description='测试内容',
            question_type='single',
            options=[{'key': 'A', 'text': 'A'}, {'key': 'B', 'text': 'B'}, {'key': 'C', 'text': 'C'}, {'key': 'D', 'text': 'D'}],
            correct_answer='A',
            difficulty='easy',
            score=10,
            category=self.category,
            created_by=self.admin_user
        )
        
        # 创建一些提交记录
        ChoiceQuestionSubmission.objects.create(
            user=self.user,
            question=self.question,
            selected_answer='A',
            is_correct=True,
            score=10,
            time_spent=30
        )
    
    def test_get_user_statistics(self):
        """测试获取用户统计信息"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('choice_question:user-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_questions', response.data)
        self.assertIn('total_correct', response.data)
        self.assertIn('accuracy', response.data)
        self.assertEqual(response.data['total_questions'], 1)
        self.assertEqual(response.data['total_correct'], 1)
    
    def test_get_admin_statistics(self):
        """测试获取管理员统计信息"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('choice_question:admin-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_questions', response.data)
        self.assertIn('total_submitted', response.data)
        self.assertIn('total_correct', response.data)
        self.assertIn('category_stats', response.data)