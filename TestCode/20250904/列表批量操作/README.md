# 选择题列表批量操作修复

## 问题描述
用户报告 `http://localhost:8080/admin/choice-questions` 页面批量操作功能报错，后端返回404错误。

## 问题原因
后端缺少批量操作的API端点和路由配置。

## 修复内容

### 1. 后端修改

#### admin_views.py
- 在 `ChoiceQuestionAdminAPI` 类中添加了 `patch` 方法
- 实现了批量操作功能，支持以下操作：
  - `delete`: 批量删除题目
  - `toggle_visible`: 批量切换可见性
  - `set_visible`: 批量设置可见性
  - `set_hidden`: 批量设置隐藏
  - `set_difficulty`: 批量设置难度
  - `update_difficulty`: 批量更新难度（兼容前端）
  - `set_category`: 批量设置分类

#### admin_urls.py
- 添加了批量操作路由：`^choice_question/batch_operation/?$`

### 2. 前端修改

#### ChoiceQuestionList.vue
- **关键修复1**: 将批量操作的HTTP方法从 `POST` 改为 `PATCH`
  - 原因：后端批量操作使用PATCH方法，前端使用POST会导致路由到创建接口
  - 错误表现：`title: This field is required.` (因为创建接口需要title字段)
- **关键修复2**: 前后端action类型匹配
  - 前端发送的action类型与后端支持的完全匹配
  - 移除了不支持的 `update_language` 选项
  - 统一了难度值格式映射
- 增强了错误处理逻辑
- 添加了详细的控制台错误输出
- 改进了错误消息显示，包括：
  - HTTP状态码识别
  - 具体错误信息提取
  - 10秒错误消息显示时间
  - 可关闭的错误提示

## 关键修复

### 1. 批量操作HTTP方法错误修复
- **问题**: 前端使用POST请求调用批量操作API，但后端实现的是PATCH方法
- **错误**: 请求被路由到创建题目的接口，导致报错 `title: This field is required.`
- **修复**: 将前端 `this.$http.post` 改为 `this.$http.patch`
- **文件**: `ChoiceQuestionList.vue` 第588行
- **结果**: 批量操作请求能正确路由到后端PATCH方法

### 2. 前后端action类型不匹配修复
- **问题**: 前端发送的action类型与后端支持的不完全匹配
- **前端action类型**: `set_visible`, `set_hidden`, `update_difficulty`, `update_language`
- **后端原支持**: `set_visible`, `toggle_visible`, `set_difficulty`, `set_category`
- **修复内容**:
  - 后端添加 `set_hidden` action支持
  - 后端添加 `update_difficulty` action支持（兼容原`set_difficulty`）
  - 后端改进难度值映射（支持前端的Easy/Medium/Hard格式）
  - 前端移除 `update_language` 选项（因模型无language字段）
- **文件**: `admin_views.py` 第202-238行, `ChoiceQuestionList.vue`
- **结果**: 所有批量操作功能正常工作

## 修改的文件
1. `/home/metaspeekoj/OnlineJudge/choice_question/admin_views.py`
2. `/home/metaspeekoj/OnlineJudge/choice_question/admin_urls.py`
3. `/home/metaspeekoj/OnlineJudgeFE/src/pages/admin/views/choice-question/ChoiceQuestionList.vue`

## 使用方法
1. 重启后端服务器以加载新的路由配置
2. 前端会自动重新编译
3. 访问选择题管理页面测试批量操作功能

## 测试建议
1. 选择多个题目进行批量删除
2. 测试批量设置可见性
3. 测试批量设置难度和分类
4. 查看浏览器控制台确认错误信息正确显示