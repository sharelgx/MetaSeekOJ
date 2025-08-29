# QDUOJ选择题插件集成指南

本文档详细说明如何将选择题插件集成到QDUOJ系统中。

## 系统要求

- QDUOJ 后端系统
- QDUOJ 前端系统
- Python 3.6+
- Django 2.1+
- Vue.js 2.6+
- Node.js 12+

## 后端集成

### 1. 复制插件代码

将 `backend/choice_question` 目录复制到 QDUOJ 后端项目的根目录下：

```bash
cp -r qduoj-choice-question-plugin/backend/choice_question /path/to/OnlineJudge/
```

### 2. 配置Django应用

在 `oj/settings.py` 中的 `LOCAL_APPS` 列表中添加选择题应用：

```python
LOCAL_APPS = [
    'account',
    'announcement',
    'conf',
    'problem',
    'contest',
    'utils',
    'submission',
    'options',
    'judge',
    'choice_question',  # 添加这一行
]
```

### 3. 配置URL路由

在 `oj/urls.py` 中添加选择题插件的URL配置：

```python
urlpatterns = [
    # ... 其他URL配置
    url(r"^api/choice-question/", include("choice_question.urls")),
    # ... 其他URL配置
]
```

### 4. 运行数据库迁移

```bash
cd /path/to/OnlineJudge
python manage.py makemigrations choice_question
python manage.py migrate
```

### 5. 安装依赖包

如果插件需要额外的Python包，请安装：

```bash
pip install openpyxl  # 用于Excel导入导出
pip install python-docx  # 如果需要Word文档支持
```

## 前端集成

### 1. 复制前端代码

将前端代码复制到QDUOJ前端项目中：

```bash
# 复制组件和视图
cp -r qduoj-choice-question-plugin/frontend/* /path/to/OnlineJudgeFE/src/pages/oj/

# 或者创建插件目录
mkdir -p /path/to/OnlineJudgeFE/src/plugins/choice-question
cp -r qduoj-choice-question-plugin/frontend/* /path/to/OnlineJudgeFE/src/plugins/choice-question/
```

### 2. 集成路由配置

#### OJ前端路由集成

在 `/path/to/OnlineJudgeFE/src/pages/oj/router/routes.js` 中添加选择题路由：

```javascript
// 导入选择题组件
import QuestionManagement from '@/plugins/choice-question/views/QuestionManagement.vue'
import QuestionAnswering from '@/plugins/choice-question/components/QuestionAnswering.vue'
import WrongQuestionBook from '@/plugins/choice-question/views/WrongQuestionBook.vue'
import QuestionStatistics from '@/plugins/choice-question/views/QuestionStatistics.vue'

// 在routes数组中添加以下路由
export default [
  // ... 现有路由
  {
    name: 'choice-question-list',
    path: '/choice-question',
    meta: { title: 'Choice Question Practice' },
    component: QuestionManagement
  },
  {
    name: 'choice-question-answering',
    path: '/choice-question/:questionId/answer',
    meta: { title: 'Answer Question', requiresAuth: true },
    component: QuestionAnswering
  },
  {
    name: 'choice-question-wrong-book',
    path: '/choice-question/wrong-book',
    meta: { title: 'Wrong Question Book', requiresAuth: true },
    component: WrongQuestionBook
  },
  {
    name: 'choice-question-statistics',
    path: '/choice-question/statistics',
    meta: { title: 'Practice Statistics', requiresAuth: true },
    component: QuestionStatistics
  },
  // ... 其他路由
]
```

#### Admin后端路由集成

在 `/path/to/OnlineJudgeFE/src/pages/admin/router.js` 中添加管理路由：

```javascript
// 导入选择题管理组件
import QuestionManagement from '@/plugins/choice-question/views/QuestionManagement.vue'
import CategoryManagement from '@/plugins/choice-question/views/CategoryManagement.vue'
import QuestionEditor from '@/plugins/choice-question/components/QuestionEditor.vue'
import QuestionStatistics from '@/plugins/choice-question/views/QuestionStatistics.vue'

// 在Home组件的children数组中添加
children: [
  // ... 现有子路由
  {
    path: '/choice-question',
    name: 'choice-question-management',
    component: QuestionManagement
  },
  {
    path: '/choice-question/create',
    name: 'create-choice-question',
    component: QuestionEditor
  },
  {
    path: '/choice-question/edit/:questionId',
    name: 'edit-choice-question',
    component: QuestionEditor
  },
  {
    path: '/choice-question/category',
    name: 'choice-question-category',
    component: CategoryManagement
  },
  {
    path: '/choice-question/statistics',
    name: 'choice-question-admin-statistics',
    component: QuestionStatistics
  }
]
```

### 3. 集成导航菜单

#### OJ前端导航栏

在 `/path/to/OnlineJudgeFE/src/pages/oj/components/NavBar.vue` 中添加菜单项：

```vue
<template>
  <div id="header">
    <Menu theme="light" mode="horizontal" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <!-- ... 现有菜单项 -->
      <Menu-item name="/choice-question">
        <Icon type="ios-list-box"></Icon>
        {{$t('m.Choice_Question_Practice')}}
      </Menu-item>
      <!-- ... 其他菜单项 -->
    </Menu>
  </div>
</template>
```

#### Admin后端侧边栏

在 `/path/to/OnlineJudgeFE/src/pages/admin/components/SideMenu.vue` 中添加菜单项：

```vue
<template>
  <el-menu class="vertical_menu" :router="true" :default-active="currentPath">
    <!-- ... 现有菜单项 -->
    <el-submenu index="choice-question" v-if="hasProblemPermission">
      <template slot="title"><i class="el-icon-fa-list-alt"></i>{{$t('m.Choice_Question_Management')}}</template>
      <el-menu-item index="/choice-question">{{$t('m.Question_Management')}}</el-menu-item>
      <el-menu-item index="/choice-question/create">{{$t('m.Create_Question')}}</el-menu-item>
      <el-menu-item index="/choice-question/category">{{$t('m.Category_Management')}}</el-menu-item>
      <el-menu-item index="/choice-question/statistics">{{$t('m.Statistics_Analysis')}}</el-menu-item>
    </el-submenu>
    <!-- ... 其他菜单项 -->
  </el-menu>
</template>
```

### 4. 添加国际化文本

在相应的国际化文件中添加文本：

#### 中文 (`/path/to/OnlineJudgeFE/src/i18n/oj/zh-CN.js`)

```javascript
export const m = {
  // ... 现有文本
  Choice_Question_Practice: '选择题练习',
  Question_Practice: '题目练习',
  Wrong_Question_Book: '错题本',
  Practice_Statistics: '练习统计',
  // ... 其他文本
}
```

#### 英文 (`/path/to/OnlineJudgeFE/src/i18n/oj/en-US.js`)

```javascript
export const m = {
  // ... 现有文本
  Choice_Question_Practice: 'Choice Question Practice',
  Question_Practice: 'Question Practice',
  Wrong_Question_Book: 'Wrong Question Book',
  Practice_Statistics: 'Practice Statistics',
  // ... 其他文本
}
```

### 5. 安装前端依赖

```bash
cd /path/to/OnlineJudgeFE
npm install
# 或
yarn install
```

## 自动化集成（推荐）

为了简化集成过程，可以使用插件提供的集成脚本：

### 1. 使用集成模块

在QDUOJ前端项目中使用插件的集成模块：

```javascript
// 在main.js或相应的入口文件中
import choiceQuestionPlugin from '@/plugins/choice-question/integration'

// 初始化插件
choiceQuestionPlugin.initializePlugin(app)

// 集成到OJ前端
choiceQuestionPlugin.integrateWithOJ(router, store, i18n)

// 或集成到Admin后端
choiceQuestionPlugin.integrateWithAdmin(router, store, i18n)
```

### 2. 运行集成脚本

```bash
# 复制并运行集成脚本
cp qduoj-choice-question-plugin/scripts/integrate.sh .
chmod +x integrate.sh
./integrate.sh
```

## 权限配置

### 1. 后端权限

选择题插件使用QDUOJ现有的权限系统：

- **普通用户**：可以答题、查看错题本、查看个人统计
- **管理员**：可以管理题目、分类、查看所有统计数据
- **超级管理员**：拥有所有权限

### 2. 前端权限控制

在路由配置中使用 `requiresAuth` 和权限检查：

```javascript
{
  name: 'choice-question-management',
  path: '/choice-question',
  meta: { 
    title: 'Question Management',
    requiresAuth: true,
    requiresAdmin: true
  },
  component: QuestionManagement
}
```

## 测试集成

### 1. 后端测试

```bash
# 运行后端服务
cd /path/to/OnlineJudge
python manage.py runserver

# 测试API接口
curl http://localhost:8000/api/choice-question/categories/
```

### 2. 前端测试

```bash
# 运行前端开发服务器
cd /path/to/OnlineJudgeFE
npm run dev

# 访问选择题页面
# http://localhost:8080/choice-question
```

## 故障排除

### 常见问题

1. **路由404错误**
   - 检查URL配置是否正确
   - 确认应用已添加到INSTALLED_APPS

2. **前端组件加载失败**
   - 检查组件路径是否正确
   - 确认依赖是否已安装

3. **数据库错误**
   - 运行数据库迁移
   - 检查数据库连接配置

4. **权限错误**
   - 检查用户权限配置
   - 确认中间件配置正确

### 日志调试

启用Django调试模式查看详细错误信息：

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'choice_question': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 更新和维护

### 插件更新

1. 备份现有数据
2. 更新插件代码
3. 运行数据库迁移
4. 重启服务

### 数据备份

```bash
# 备份选择题相关数据
python manage.py dumpdata choice_question > choice_question_backup.json

# 恢复数据
python manage.py loaddata choice_question_backup.json
```

## 支持和反馈

如果在集成过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查QDUOJ官方文档
3. 在GitHub上提交Issue
4. 联系开发团队

---

**注意**：本插件基于QDUOJ系统开发，请确保您的QDUOJ系统版本兼容。建议在测试环境中先进行集成测试，确认无误后再部署到生产环境。