# 青岛OJ选择题插件

## 概述

青岛OJ选择题插件为青岛大学在线判题系统（QDUOJ）提供完整的选择题功能，支持单选题和多选题的创建、管理、答题、统计等功能。该插件采用模块化设计，可以轻松集成到现有的青岛OJ系统中。

## 功能特性

### 📝 题目管理
- **多种题型**：支持单选题和多选题
- **分类管理**：支持题目分类，便于组织和管理
- **标签系统**：支持多标签标记，方便筛选和搜索
- **难度等级**：支持简单、中等、困难三个难度等级
- **富文本编辑**：支持题目内容的富文本编辑
- **批量导入**：支持批量导入题目（计划功能）

### 🎯 答题功能
- **在线答题**：支持在线选择答案并提交
- **自动评分**：自动判断答案正确性并计算得分
- **答案解析**：提供详细的答案解析
- **提交记录**：完整记录用户的答题历史
- **重复答题**：支持同一题目多次答题

### 📚 错题本
- **错题收集**：自动收集用户答错的题目
- **错题重做**：支持错题重新练习
- **笔记功能**：支持为错题添加个人笔记
- **错题统计**：统计错题的错误次数和时间

### 📊 统计分析
- **个人统计**：个人答题数量、正确率等统计
- **题目统计**：题目的答题人数、正确率等统计
- **分类统计**：按分类统计答题情况
- **趋势分析**：答题趋势和进步情况分析

### 🔐 权限管理
- **角色权限**：区分管理员和普通用户权限
- **题目权限**：支持题目的查看、编辑、删除权限控制
- **数据安全**：确保用户数据的安全性和隐私性

## 系统要求

### 后端要求
- Python >= 3.6
- Django >= 2.2.0
- 青岛OJ >= 2.0.0

### 前端要求
- Node.js >= 12.0.0
- Vue.js >= 2.6.0
- Element UI >= 2.0.0

## 安装指南

### 自动安装（推荐）

1. 下载插件到青岛OJ同级目录：
```bash
git clone https://github.com/QingdaoU/qduoj-choice-question-plugin.git
cd qduoj-choice-question-plugin
```

2. 运行安装脚本：
```bash
./scripts/install.sh [QDUOJ_PATH] [QDUOJ_FE_PATH]
```

例如：
```bash
./scripts/install.sh /home/user/OnlineJudge /home/user/OnlineJudgeFE
```

3. 重启服务：
```bash
# 重启Django服务器
cd /path/to/OnlineJudge
python3 manage.py runserver

# 重新构建前端
cd /path/to/OnlineJudgeFE
npm run build
```

### 手动安装

#### 后端安装

1. 复制后端文件：
```bash
cp -r backend/choice_question /path/to/OnlineJudge/
```

2. 修改 `settings.py`：
```python
INSTALLED_APPS = [
    # ... 其他应用
    'choice_question',
]
```

3. 修改 `urls.py`：
```python
urlpatterns = [
    # ... 其他路由
    path('api/choice-question/', include('choice_question.urls')),
]
```

4. 运行数据库迁移：
```bash
python3 manage.py makemigrations choice_question
python3 manage.py migrate
```

#### 前端安装

1. 复制前端文件：
```bash
cp -r frontend/* /path/to/OnlineJudgeFE/src/pages/oj/views/choice-question/
```

2. 添加路由配置到 `router/routes.js`：
```javascript
// 选择题模块路由
{
  name: 'choice-question-list',
  path: '/choice-questions',
  component: () => import('@oj/views/choice-question/ChoiceQuestionList.vue'),
  meta: { title: '选择题练习', requiresAuth: true }
},
{
  name: 'choice-question-detail',
  path: '/choice-questions/:id',
  component: () => import('@oj/views/choice-question/ChoiceQuestionDetail.vue'),
  meta: { title: '选择题详情', requiresAuth: true }
},
{
  name: 'wrong-question-book',
  path: '/wrong-questions',
  component: () => import('@oj/views/choice-question/WrongQuestionBook.vue'),
  meta: { title: '错题本', requiresAuth: true }
}
```

3. 添加菜单配置（可选）

## 使用指南

### 管理员使用

1. **创建分类和标签**：
   - 访问 Django 管理后台
   - 在「选择题模块」中创建分类和标签

2. **创建题目**：
   - 在管理后台创建选择题
   - 设置题目内容、选项、正确答案等

3. **权限管理**：
   - 为用户分配相应的权限
   - 控制题目的访问和编辑权限

### 用户使用

1. **浏览题目**：
   - 访问 `/choice-questions` 查看题目列表
   - 使用筛选功能查找特定题目

2. **答题练习**：
   - 点击题目进入答题页面
   - 选择答案并提交
   - 查看答案解析和得分

3. **错题管理**：
   - 访问 `/wrong-questions` 查看错题本
   - 重做错题并添加笔记

## API 文档

### 题目相关 API

- `GET /api/choice-question/questions/` - 获取题目列表
- `GET /api/choice-question/questions/{id}/` - 获取题目详情
- `POST /api/choice-question/questions/` - 创建题目（管理员）
- `PUT /api/choice-question/questions/{id}/` - 更新题目（管理员）
- `DELETE /api/choice-question/questions/{id}/` - 删除题目（管理员）

### 分类和标签 API

- `GET /api/choice-question/categories/` - 获取分类列表
- `GET /api/choice-question/tags/` - 获取标签列表

### 答题相关 API

- `POST /api/choice-question/submissions/` - 提交答案
- `GET /api/choice-question/submissions/` - 获取提交记录

### 错题本 API

- `GET /api/choice-question/wrong-questions/` - 获取错题列表
- `POST /api/choice-question/wrong-questions/` - 添加错题
- `DELETE /api/choice-question/wrong-questions/{id}/` - 移除错题

### 统计 API

- `GET /api/choice-question/stats/` - 获取统计信息

## 配置选项

在 `settings.py` 中可以配置以下选项：

```python
# 选择题插件配置
CHOICE_QUESTION_PAGE_SIZE = 20  # 分页大小
CHOICE_QUESTION_MAX_TAGS = 10   # 最大标签数量
CHOICE_QUESTION_ALLOW_ANONYMOUS = False  # 是否允许匿名访问
```

## 卸载指南

### 自动卸载

```bash
./scripts/uninstall.sh [QDUOJ_PATH] [QDUOJ_FE_PATH]
```

### 手动卸载

1. 从 `settings.py` 中移除 `choice_question`
2. 从 `urls.py` 中移除相关路由
3. 删除前端文件
4. 删除后端文件
5. 清理数据库（可选）

## 故障排除

### 常见问题

1. **安装后无法访问页面**
   - 检查路由配置是否正确
   - 确认服务器已重启
   - 检查权限设置

2. **数据库迁移失败**
   - 检查数据库连接
   - 确认Django版本兼容性
   - 查看详细错误信息

3. **前端页面显示异常**
   - 检查前端文件是否正确复制
   - 确认Vue组件路径
   - 检查浏览器控制台错误

### 日志查看

- Django日志：查看Django服务器输出
- 前端日志：查看浏览器开发者工具控制台
- 数据库日志：查看数据库相关日志

## 开发指南

### 目录结构

```
qduoj-choice-question-plugin/
├── backend/                 # 后端代码
│   ├── choice_question/     # Django应用
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # API视图
│   │   ├── serializers.py   # 序列化器
│   │   ├── urls.py          # URL路由
│   │   └── admin.py         # 管理后台
│   └── requirements.txt     # 后端依赖
├── frontend/                # 前端代码
│   ├── views/               # Vue页面组件
│   ├── components/          # Vue子组件
│   ├── api/                 # API接口
│   ├── router/              # 路由配置
│   └── store/               # Vuex状态管理
├── docs/                    # 文档
├── scripts/                 # 安装脚本
└── plugin.json              # 插件配置
```

### 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

MIT License

## 支持

- 项目主页：https://github.com/QingdaoU/OnlineJudge
- 问题反馈：https://github.com/QingdaoU/qduoj-choice-question-plugin/issues
- 文档：https://docs.onlinejudge.me/

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持单选题和多选题
- 完整的答题和统计功能
- 错题本功能
- 管理后台集成