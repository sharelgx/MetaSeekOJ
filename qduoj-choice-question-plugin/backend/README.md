# 选择题插件后端模块

## 概述

本模块为青岛OJ系统提供选择题功能，包括选择题的创建、管理、答题、统计等功能。

## 功能特性

- **题目管理**：支持单选题和多选题的创建和管理
- **分类标签**：支持题目分类和标签系统
- **难度等级**：支持简单、中等、困难三个难度等级
- **答题功能**：支持用户答题和自动评分
- **错题本**：支持错题收集和重做功能
- **统计分析**：提供详细的答题统计信息

## 数据模型

### ChoiceQuestionCategory (选择题分类)
- `name`: 分类名称
- `description`: 分类描述
- `created_time`: 创建时间

### ChoiceQuestionTag (选择题标签)
- `name`: 标签名称
- `color`: 标签颜色
- `created_time`: 创建时间

### ChoiceQuestion (选择题)
- `title`: 题目标题
- `content`: 题目内容
- `options`: 选项（JSON格式）
- `correct_answer`: 正确答案
- `explanation`: 答案解析
- `category`: 所属分类
- `tags`: 关联标签
- `difficulty`: 难度等级
- `question_type`: 题目类型（单选/多选）
- `score`: 分值
- `created_by`: 创建者
- `created_time`: 创建时间
- `last_update_time`: 最后更新时间

### ChoiceQuestionSubmission (选择题提交记录)
- `user`: 提交用户
- `question`: 关联题目
- `selected_answer`: 选择的答案
- `is_correct`: 是否正确
- `score`: 得分
- `submit_time`: 提交时间

### WrongQuestion (错题本)
- `user`: 用户
- `question`: 错题
- `wrong_count`: 错误次数
- `note`: 笔记
- `added_time`: 加入时间
- `last_wrong_time`: 最后错误时间

## API接口

### 分类管理
- `GET /api/choice-question/categories/` - 获取分类列表
- `POST /api/choice-question/categories/` - 创建分类
- `PUT /api/choice-question/categories/{id}/` - 更新分类
- `DELETE /api/choice-question/categories/{id}/` - 删除分类

### 标签管理
- `GET /api/choice-question/tags/` - 获取标签列表
- `POST /api/choice-question/tags/` - 创建标签
- `PUT /api/choice-question/tags/{id}/` - 更新标签
- `DELETE /api/choice-question/tags/{id}/` - 删除标签

### 选择题管理
- `GET /api/choice-question/questions/` - 获取题目列表
- `POST /api/choice-question/questions/` - 创建题目
- `GET /api/choice-question/questions/{id}/` - 获取题目详情
- `PUT /api/choice-question/questions/{id}/` - 更新题目
- `DELETE /api/choice-question/questions/{id}/` - 删除题目

### 答题功能
- `POST /api/choice-question/submissions/` - 提交答案
- `GET /api/choice-question/submissions/` - 获取提交记录

### 错题本
- `GET /api/choice-question/wrong-questions/` - 获取错题列表
- `POST /api/choice-question/wrong-questions/` - 添加错题
- `DELETE /api/choice-question/wrong-questions/{id}/` - 移除错题

### 统计信息
- `GET /api/choice-question/stats/` - 获取统计信息

## 安装说明

1. 将本模块复制到青岛OJ项目目录
2. 在 `settings.py` 中添加应用配置
3. 在主 `urls.py` 中添加路由配置
4. 运行数据库迁移
5. 创建超级用户并在管理后台配置

## 权限说明

- 管理员：可以创建、编辑、删除所有题目和分类
- 普通用户：可以查看题目、提交答案、管理个人错题本