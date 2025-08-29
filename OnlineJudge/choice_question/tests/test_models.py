from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from choice_question.models import (
    Category,
    ChoiceQuestion,
    WrongQuestion,
    ChoiceQuestionSubmission,
    QuestionTag,
)

# Create aliases for backward compatibility with test names
ChoicePluginCategory = Category
ChoicePluginQuestion = ChoiceQuestion
ChoicePluginWrongQuestion = WrongQuestion
ChoicePluginSubmission = ChoiceQuestionSubmission
ChoicePluginQuestionTag = QuestionTag
# Note: ChoicePluginQuestionTagRelation doesn't exist in current models

User = get_user_model()


class ChoicePluginCategoryModelTest(TestCase):
    """选择题分类模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_category(self):
        """测试创建分类"""
        category = ChoicePluginCategory.objects.create(
            name='数学',
            description='数学相关题目'
        )
        
        self.assertEqual(category.name, '数学')
        self.assertEqual(category.description, '数学相关题目')
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)
        self.assertEqual(category.order, 0)
    
    def test_category_hierarchy(self):
        """测试分类层级关系"""
        parent_category = ChoicePluginCategory.objects.create(
            name='理科'
        )
        
        child_category = ChoicePluginCategory.objects.create(
            name='数学',
            parent=parent_category
        )
        
        self.assertEqual(child_category.parent, parent_category)
        self.assertIn(child_category, parent_category.children.all())
    
    def test_category_str_representation(self):
        """测试分类字符串表示"""
        category = ChoicePluginCategory.objects.create(
            name='物理'
        )
        
        self.assertEqual(str(category), '物理')
    
    def test_category_unique_name_per_parent(self):
        """测试同一父分类下可以创建同名分类（当前模型没有唯一性约束）"""
        parent = ChoicePluginCategory.objects.create(
            name='理科'
        )
        
        ChoicePluginCategory.objects.create(
            name='数学',
            parent=parent
        )
        
        # 可以创建同名分类（模型没有唯一性约束）
        duplicate_category = ChoicePluginCategory.objects.create(
            name='数学',
            parent=parent
        )
        
        self.assertEqual(duplicate_category.name, '数学')
        self.assertEqual(duplicate_category.parent, parent)


class ChoicePluginQuestionModelTest(TestCase):
    """选择题模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ChoicePluginCategory.objects.create(
            name='数学'
        )
    
    def test_create_single_choice_question(self):
        """测试创建单选题"""
        question = ChoicePluginQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',  # 正确答案是'2'
            difficulty='easy',
            score=10,
            category=self.category
        )
        
        self.assertEqual(question.title, '1+1等于多少？')
        self.assertEqual(question.question_type, 'single')
        self.assertEqual(len(question.options), 4)
        self.assertEqual(question.correct_answer, 'B')
        self.assertEqual(question.difficulty, 'easy')
        self.assertEqual(question.score, 10)
        self.assertEqual(question.category, self.category)
        self.assertTrue(question.visible)
    
    def test_create_multiple_choice_question(self):
        """测试创建多选题"""
        question = ChoicePluginQuestion.objects.create(
            title='以下哪些是质数？',
            description='请选择所有正确答案',
            question_type='multiple',
            options=[{'key': 'A', 'text': '2'}, {'key': 'B', 'text': '3'}, {'key': 'C', 'text': '4'}, {'key': 'D', 'text': '5'}],
            correct_answer='A,B,D',  # 2, 3, 5都是质数
            difficulty='medium',
            score=20,
            category=self.category
        )
        
        self.assertEqual(question.question_type, 'multiple')
        self.assertEqual(question.correct_answer, 'A,B,D')
        self.assertEqual(question.score, 20)
    
    def test_question_validation(self):
        """测试题目验证"""
        # 测试选项数量验证
        with self.assertRaises(ValidationError):
            question = ChoicePluginQuestion(
                title='测试题',
                description='测试内容',
                question_type='single',
                options=[{'key': 'A', 'text': 'Option A'}],  # 选项太少
                correct_answer='A',
                category=self.category
            )
            question.full_clean()
        
        # 测试正确答案索引验证
        with self.assertRaises(ValidationError):
            question = ChoicePluginQuestion(
                title='测试题',
                description='测试内容',
                question_type='single',
                options=[{'key': 'A', 'text': 'Option A'}, {'key': 'B', 'text': 'Option B'}],
                correct_answer='Z',  # 不存在的选项
                category=self.category
            )
            question.full_clean()
    
    def test_question_str_representation(self):
        """测试题目字符串表示"""
        question = ChoicePluginQuestion.objects.create(
            _id='TEST001',
            title='测试题目',
            description='测试内容',
            question_type='single',
            options=[{'key': 'A', 'text': 'Option A'}, {'key': 'B', 'text': 'Option B'}, {'key': 'C', 'text': 'Option C'}, {'key': 'D', 'text': 'Option D'}],
            correct_answer='A',
            category=self.category
        )
        
        self.assertEqual(str(question), '[TEST001] 测试题目')


class ChoicePluginSubmissionModelTest(TestCase):
    """选择题提交记录模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ChoicePluginCategory.objects.create(
            name='数学'
        )
        
        self.question = ChoicePluginQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',
            difficulty='easy',
            score=10,
            category=self.category
        )
    
    def test_create_correct_submission(self):
        """测试创建正确答案的提交记录"""
        submission = ChoicePluginSubmission.objects.create(
            user=self.user,
            question=self.question,
            selected_answer='B',
            is_correct=True,
            score=10,
            time_spent=30
        )
        
        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.question, self.question)
        self.assertEqual(submission.selected_answer, 'B')
        self.assertTrue(submission.is_correct)
        self.assertEqual(submission.score, 10)
        self.assertEqual(submission.time_spent, 30)
    
    def test_create_incorrect_submission(self):
        """测试创建错误答案的提交记录"""
        submission = ChoicePluginSubmission.objects.create(
            user=self.user,
            question=self.question,
            selected_answer='A',
            is_correct=False,
            score=0,
            time_spent=45
        )
        
        self.assertEqual(submission.selected_answer, 'A')
        self.assertFalse(submission.is_correct)
        self.assertEqual(submission.score, 0)
    
    def test_submission_str_representation(self):
        """测试提交记录字符串表示"""
        submission = ChoicePluginSubmission.objects.create(
            user=self.user,
            question=self.question,
            selected_answer='B',
            is_correct=True,
            score=10
        )
        
        expected_str = f'{self.user.username} - {self.question.title} - 正确'
        self.assertEqual(str(submission), expected_str)


class ChoicePluginWrongQuestionModelTest(TestCase):
    """错题记录模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ChoicePluginCategory.objects.create(
            name='数学'
        )
        
        self.question = ChoicePluginQuestion.objects.create(
            title='1+1等于多少？',
            description='请选择正确答案',
            question_type='single',
            options=[{'key': 'A', 'text': '1'}, {'key': 'B', 'text': '2'}, {'key': 'C', 'text': '3'}, {'key': 'D', 'text': '4'}],
            correct_answer='B',
            difficulty='easy',
            score=10,
            category=self.category
        )
    
    def test_create_wrong_question_record(self):
        """测试创建错题记录"""
        wrong_question = ChoicePluginWrongQuestion.objects.create(
            user=self.user,
            question=self.question,
            wrong_count=1,
            last_wrong_answer='A'
        )
        
        self.assertEqual(wrong_question.user, self.user)
        self.assertEqual(wrong_question.question, self.question)
        self.assertEqual(wrong_question.wrong_count, 1)
        self.assertEqual(wrong_question.last_wrong_answer, 'A')
        self.assertFalse(wrong_question.is_mastered)
    
    def test_resolve_wrong_question(self):
        """测试解决错题"""
        wrong_question = ChoicePluginWrongQuestion.objects.create(
            user=self.user,
            question=self.question,
            wrong_count=2,
            last_wrong_answer='A'
        )
        
        # 标记为已掌握
        wrong_question.is_mastered = True
        wrong_question.save()
        
        self.assertTrue(wrong_question.is_mastered)
    
    def test_wrong_question_unique_constraint(self):
        """测试错题记录唯一性约束"""
        ChoicePluginWrongQuestion.objects.create(
            user=self.user,
            question=self.question,
            wrong_count=1
        )
        
        # 尝试创建重复记录应该失败
        with self.assertRaises(IntegrityError):
            ChoicePluginWrongQuestion.objects.create(
                user=self.user,
                question=self.question,
                wrong_count=1
            )


class ChoicePluginQuestionTagModelTest(TestCase):
    """题目标签模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_tag(self):
        """测试创建标签"""
        tag = ChoicePluginQuestionTag.objects.create(
            name='代数',
            color='#FF5722'
        )
        
        self.assertEqual(tag.name, '代数')
        self.assertEqual(tag.color, '#FF5722')
        # Note: created_by field doesn't exist in QuestionTag model
    
    def test_tag_unique_name(self):
        """测试标签名称唯一性"""
        ChoicePluginQuestionTag.objects.create(
            name='几何'
        )
        
        # 尝试创建同名标签应该失败
        with self.assertRaises(IntegrityError):
            ChoicePluginQuestionTag.objects.create(
                name='几何'
            )
    
    def test_tag_str_representation(self):
        """测试标签字符串表示"""
        tag = ChoicePluginQuestionTag.objects.create(
            name='概率'
        )
        
        self.assertEqual(str(tag), '概率')


class ChoicePluginQuestionTagRelationModelTest(TestCase):
    """题目标签关系模型测试 - 使用 ManyToMany 关系"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ChoicePluginCategory.objects.create(
            name='数学'
        )
        
        self.question = ChoicePluginQuestion.objects.create(
            title='测试题目',
            description='测试内容',
            question_type='single',
            options=[{'key': 'A', 'text': 'Option A'}, {'key': 'B', 'text': 'Option B'}],
            correct_answer='A',
            category=self.category
        )
        
        self.tag = ChoicePluginQuestionTag.objects.create(
            name='代数'
        )
    
    def test_create_tag_relation(self):
        """测试创建标签关系"""
        self.question.tags.add(self.tag)
        
        self.assertIn(self.tag, self.question.tags.all())
        self.assertEqual(self.question.tags.count(), 1)
    
    def test_tag_relation_unique_constraint(self):
        """测试标签关系唯一性约束"""
        self.question.tags.add(self.tag)
        
        # ManyToMany 关系自动处理重复，不会抛出异常
        self.question.tags.add(self.tag)
        self.assertEqual(self.question.tags.count(), 1)