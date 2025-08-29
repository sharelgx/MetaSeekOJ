## ✅ 给Trae的确认和下一步指令

```markdown
# 确认和明确开发方向

## 确认理解
很好！你的调研报告很全面。确认一下我们的开发方向：

1. ✅ 我们是在**青岛OJ现有系统**基础上开发选择题模块
2. ✅ 不是独立的Django项目，而是青岛OJ的一个扩展模块
3. ✅ 必须使用青岛OJ已有的：
   - `utils.api.APIView` 基类（不是Django原生的APIView）
   - 青岛OJ的用户系统（account模块）
   - 青岛OJ的权限系统
   - 青岛OJ的前端组件和样式

## 关键发现确认
从你的调研中，我注意到几个重要点：

1. **API基类**：青岛OJ使用自定义的 `utils.api.APIView`，有统一的响应格式：
   - `self.success(data)` - 成功响应
   - `self.error(msg)` - 错误响应  
   - `self.paginate_data()` - 分页处理

2. **模型设计**：
   - 使用 `_id` 作为显示ID（不是默认的id）
   - 使用 `JSONField` 存储复杂数据
   - 有 `create_time` 等时间字段

3. **前端架构**：
   - 主要使用 iView 组件库
   - 路由在 `src/pages/oj/router/routes.js`
   - API在 `src/pages/oj/api.js`

markdown# 第一步：创建插件基础结构和Django App

## 任务目标
创建选择题插件的基础项目结构，并初始化Django应用。

## 具体任务

### 1. 创建插件目录结构
请在青岛OJ项目的同级目录创建以下插件文件夹结构：
qduoj-choice-question-plugin/
├── backend/
│   ├── choice_question/
│   │   ├── init.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── components/
│   ├── views/
│   ├── api/
│   ├── router/
│   └── store/
├── docs/
│   └── README.md
├── scripts/
│   ├── install.sh
│   └── uninstall.sh
└── plugin.json

## 下一步任务：创建选择题数据模型

基于调研结果，现在请创建选择题模块的数据模型。

### 任务：在 choice_question/models.py 中创建模型

请参考青岛OJ的Problem模型风格，创建以下模型：

```python
# choice_question/models.py

from django.db import models
from django.contrib.postgres.fields import JSONField
from account.models import User
from utils.models import RichTextField
from django.utils import timezone

class ChoiceQuestionCategory(models.Model):
    """选择题分类（支持多级）"""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, 
                              on_delete=models.CASCADE, 
                              related_name='children')
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "choice_question_category"
        ordering = ("order", "id")

class ChoiceQuestionTag(models.Model):
    """选择题标签"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#409EFF')
    
    class Meta:
        db_table = "choice_question_tag"

class ChoiceQuestion(models.Model):
    """选择题模型"""
    # 参考Problem模型的设计
    _id = models.CharField(max_length=32, db_index=True)  # 显示ID
    title = models.TextField()
    description = RichTextField()  # 使用青岛OJ的富文本字段
    
    # 题目类型
    QUESTION_TYPE = (
        ("single", "Single Choice"),
        ("multiple", "Multiple Choice"),
    )
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE)
    
    # 选项存储为JSON
    options = JSONField()  # [{"key": "A", "text": "选项内容"}, ...]
    correct_answer = models.CharField(max_length=10)  # "A" 或 "A,B,C"
    explanation = RichTextField(blank=True)  # 答案解析
    
    # 分类和标签
    category = models.ForeignKey(ChoiceQuestionCategory, 
                                on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(ChoiceQuestionTag)
    
    # 难度和分值
    difficulty = models.CharField(max_length=10)
    score = models.IntegerField(default=10)
    
    # 统计信息
    total_submit = models.IntegerField(default=0)
    total_accepted = models.IntegerField(default=0)
    
    # 创建信息
    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                  null=True, related_name="created_choice_questions")
    
    # 状态
    visible = models.BooleanField(default=True)
    
    class Meta:
        db_table = "choice_question"
        ordering = ("-create_time",)

class ChoiceQuestionSubmission(models.Model):
    """选择题提交记录"""
    question = models.ForeignKey(ChoiceQuestion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=10)
    is_correct = models.BooleanField()
    score = models.IntegerField(default=0)
    submit_time = models.DateTimeField(auto_now_add=True)
    time_spent = models.IntegerField(default=0)  # 答题用时（秒）
    
    class Meta:
        db_table = "choice_question_submission"
        ordering = ("-submit_time",)

class WrongQuestion(models.Model):
    """错题本"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(ChoiceQuestion, on_delete=models.CASCADE)
    wrong_count = models.IntegerField(default=1)
    last_wrong_time = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
    is_mastered = models.BooleanField(default=False)
    
    class Meta:
        db_table = "choice_question_wrong"
        unique_together = ["user", "question"]
```

### 完成标准：
1. ✅ 模型遵循青岛OJ的命名规范
2. ✅ 使用青岛OJ的User模型
3. ✅ 使用青岛OJ的RichTextField（如果存在）
4. ✅ 表名使用db_table指定
5. ✅ 包含必要的索引和约束

### 执行步骤：
1. 创建上述模型文件
2. 运行 `python manage.py makemigrations choice_question`
3. 运行 `python manage.py migrate choice_question`
4. 确认数据库表创建成功

完成后，告诉我迁移是否成功，然后我们继续下一步。
```

这样明确告诉Trae：
1. 我们是在青岛OJ系统内开发
2. 必须使用青岛OJ的基类和工具
3. 遵循青岛OJ的代码规范

您觉得这样清楚吗？