# 选择题系统文件包说明文档

## 概述

本压缩包包含了在线判题系统(OnlineJudge)中选择题功能的完整实现，包括前端Vue.js组件和后端Django模块。该系统支持练习模式和考试模式两种答题方式。

## 文件夹结构

```
choice-question-files/
├── frontend/           # 前端Vue.js组件
│   ├── choice-question/
│   │   ├── ChoiceQuestionList.vue      # 选择题列表页面
│   │   ├── ChoiceQuestionDetail.vue    # 选择题详情页面
│   │   ├── PracticeMode.vue           # 练习模式页面 ⭐
│   │   ├── ExamPaper.vue              # 考试模式页面 ⭐
│   │   ├── ExamResult.vue             # 考试结果页面 ⭐
│   │   ├── ExamHistory.vue            # 考试历史页面
│   │   ├── WrongQuestionBook.vue      # 错题本页面
│   │   ├── components/                # 子组件
│   │   │   ├── AnswerSheet.vue        # 答题卡组件
│   │   │   ├── CategoryTree.vue       # 分类树组件
│   │   │   ├── QuestionCard.vue       # 题目卡片组件
│   │   │   ├── QuestionFilter.vue     # 题目筛选组件
│   │   │   └── StatisticsChart.vue    # 统计图表组件
│   │   ├── api/
│   │   │   └── index.js               # API接口定义
│   │   ├── constants.js               # 常量定义
│   │   └── index.js                   # 模块入口文件
├── backend/            # 后端Django模块
│   ├── choice_question/
│   │   ├── models/                    # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 基础模型
│   │   │   ├── category.py            # 分类模型
│   │   │   ├── exam.py                # 考试模型 ⭐
│   │   │   ├── question.py            # 题目模型
│   │   │   ├── submission.py          # 提交记录模型
│   │   │   ├── tag.py                 # 标签模型
│   │   │   └── wrong_question.py      # 错题模型
│   │   ├── views/                     # API视图
│   │   ├── serializers/               # 序列化器
│   │   ├── urls.py                    # URL路由
│   │   ├── admin.py                   # 管理后台
│   │   └── migrations/                # 数据库迁移文件
└── README.md           # 本说明文档
```

## 核心功能说明

### 1. 练习模式 (Practice Mode) ⭐

**文件位置**: `frontend/choice-question/PracticeMode.vue`

**功能特性**:
- 逐题练习，支持单选题和多选题
- 实时显示答题进度和正确率
- 支持题目筛选（按分类、标签、难度、题型）
- 答题后立即显示结果和解析
- 支持暂停/继续功能
- 答题卡导航，可快速跳转到任意题目
- 答题统计和时间记录
- 错题自动收集

**核心组件**:
- 答题界面：支持选项选择和答案提交
- 进度条：显示整体答题进度
- 答题卡：网格式题目导航
- 统计面板：实时显示答题数据

### 2. 考试模式 (Exam Mode) ⭐

**文件位置**: 
- `frontend/choice-question/ExamPaper.vue` - 考试答题页面
- `frontend/choice-question/ExamResult.vue` - 考试结果页面
- `backend/choice_question/models/exam.py` - 考试相关数据模型

**功能特性**:
- 试卷形式答题，支持限时考试
- 倒计时功能，时间不足时自动提醒
- 答题卡显示所有题目状态
- 支持题目标记和快速跳转
- 考试结束后统一提交
- 详细的考试结果分析
- 错题统计和分析
- 考试历史记录

**考试流程**:
1. 选择试卷或创建随机试卷
2. 设置考试时间限制
3. 开始考试，系统自动计时
4. 答题过程中可标记题目
5. 时间到或手动提交
6. 查看详细的考试结果

### 3. 题目管理

**功能特性**:
- 题目列表展示和筛选
- 题目详情查看
- 分类和标签管理
- 难度等级设置
- 题目统计信息

### 4. 错题本功能

**文件位置**: `frontend/choice-question/WrongQuestionBook.vue`

**功能特性**:
- 自动收集练习和考试中的错题
- 错题分类和统计
- 支持错题重做
- 错题解析查看

## 技术实现

### 前端技术栈
- **框架**: Vue.js 2.x
- **UI组件**: iView UI
- **状态管理**: Vuex
- **路由**: Vue Router
- **HTTP请求**: Axios

### 后端技术栈
- **框架**: Django
- **数据库**: 支持MySQL/PostgreSQL
- **API**: Django REST Framework
- **认证**: 基于Token的用户认证

### 数据模型关系
- `ChoiceQuestion`: 选择题基础模型
- `ExamPaper`: 试卷模型，包含多个题目
- `ExamSession`: 考试会话，记录用户考试过程
- `ChoiceQuestionSubmission`: 答题记录
- `WrongQuestion`: 错题记录

## 部署说明

### 前端部署
1. 将`frontend/choice-question/`目录复制到Vue.js项目的`src/pages/oj/views/`目录下
2. 在路由配置中添加相应的路由规则
3. 确保已安装iView UI组件库

### 后端部署
1. 将`backend/choice_question/`目录复制到Django项目中
2. 在`settings.py`中添加应用到`INSTALLED_APPS`
3. 运行数据库迁移：`python manage.py migrate`
4. 在主URL配置中包含choice_question的URL

## API接口

### 练习模式相关
- `GET /api/choice-question/questions/` - 获取题目列表
- `POST /api/choice-question/submit/` - 提交答案
- `GET /api/choice-question/statistics/` - 获取统计信息

### 考试模式相关
- `GET /api/choice-question/exam-papers/` - 获取试卷列表
- `POST /api/choice-question/exam-sessions/` - 创建考试会话
- `POST /api/choice-question/exam-submit/` - 提交考试答案
- `GET /api/choice-question/exam-results/{id}/` - 获取考试结果

## 使用说明

### 练习模式使用流程
1. 访问选择题列表页面 (`http://localhost:8080/choice-questions`)
2. 点击"练习模式"按钮
3. 可选择筛选条件（分类、难度等）
4. 开始逐题练习，查看实时反馈
5. 完成后查看统计结果

### 考试模式使用流程
1. 在选择题列表页面点击"考试模式"按钮
2. 选择试卷或设置随机出题条件
3. 设置考试时间限制
4. 开始考试，在限定时间内完成答题
5. 提交后查看详细的考试结果分析

## 特色功能

1. **智能答题卡**: 网格式布局，直观显示答题状态
2. **实时统计**: 答题过程中实时更新正确率和用时
3. **灵活筛选**: 支持多维度题目筛选
4. **错题收集**: 自动收集错题，支持针对性练习
5. **考试分析**: 详细的考试结果分析和错题统计
6. **响应式设计**: 支持PC和移动端访问

## 版本信息

- 创建时间: 2024年
- 适用系统: 青岛大学在线判题系统 (QDU OnlineJudge)
- 兼容版本: Vue.js 2.x + Django 3.x+

---

**注意**: 本文件包仅包含选择题功能的核心代码，部署时需要确保相关依赖和配置正确。