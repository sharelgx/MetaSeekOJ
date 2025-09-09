# 试卷管理页面认证问题解决方案

## 问题描述
在 http://localhost:8080/admin/exam-papers 页面点击"创建试卷"按钮时，总是重定向到登录页面。

## 问题根源
1. **API路径错误**：试卷相关的API使用的是 `/api/plugin/choice/exam-papers/` 而不是 `/api/admin/exam-papers/`
2. **认证处理不一致**：前端对认证错误的处理逻辑分散在多处，导致处理不一致
3. **路由守卫异步问题**：路由守卫中的异步认证检查可能导致组件加载时状态不一致

## 解决方案实施

### 1. 修复API路径 (已完成)
文件：`OnlineJudgeFE/src/pages/admin/api.js`

```javascript
// 试卷管理相关API
getExamPaperList (params) {
  // 注意：试卷API使用plugin路径而不是admin路径
  return ajax('plugin/choice/exam-papers/', 'get', {
    params
  })
},
createExamPaper (data) {
  // 注意：试卷API使用plugin路径而不是admin路径
  console.log('Creating exam paper with data:', data)
  return ajax('plugin/choice/exam-papers/', 'post', {
    data
  })
}
```

### 2. 优化路由守卫 (已完成)
文件：`OnlineJudgeFE/src/pages/admin/index.js`

- 将路由守卫改为 async/await 模式，确保认证检查完成后再加载组件
- 添加管理员权限检查
- 优化错误处理，清除过期的认证信息

### 3. 添加请求和响应拦截器 (已完成)
文件：`OnlineJudgeFE/src/pages/admin/api.js`

- 添加请求拦截器确保发送cookies
- 添加响应拦截器统一处理401/403认证错误
- 避免重复跳转到登录页

### 4. 优化组件认证检查 (已完成)
文件：`OnlineJudgeFE/src/pages/admin/views/choice-question/ExamPaperList.vue`

- 添加 `checkAuth` 方法统一处理认证检查
- 在 `mounted` 钩子中先检查认证再加载数据
- 优化 `createPaper` 方法的错误处理

## 测试步骤

1. **清除浏览器缓存**
   - 打开开发者工具 (F12)
   - 右键刷新按钮，选择"清空缓存并硬性重新加载"

2. **重新登录**
   - 访问 http://localhost:8080/admin/login
   - 使用管理员账号登录（root/rootroot）

3. **测试创建试卷**
   - 访问 http://localhost:8080/admin/exam-papers
   - 点击"创建试卷"按钮
   - 填写表单信息：
     - 试卷标题：测试试卷
     - 分类：选择一个分类
     - 试卷类型：固定题目
     - 考试时长：60分钟
     - 总分：100分
     - 题目数量：10题
   - 点击"创建"按钮

4. **验证结果**
   - 如果成功创建，会显示成功提示并刷新列表
   - 如果失败，查看控制台日志了解详细错误

## 调试信息

### 控制台查看要点
1. **Network标签**：
   - 查看 `/api/plugin/choice/exam-papers/` POST请求
   - 检查请求头中的Cookie（应包含sessionid和csrftoken）
   - 查看响应状态码和内容

2. **Console标签**：
   - 查看API调用日志
   - 查看路由守卫日志
   - 查看错误信息

### 常见问题排查

1. **401/403错误**：
   - 检查是否已登录
   - 检查用户是否有管理员权限
   - 检查session是否过期

2. **404错误**：
   - 检查API路径是否正确
   - 检查后端服务是否正常运行

3. **CSRF错误**：
   - 检查请求头中的X-CSRFToken
   - 检查cookies中的csrftoken

## 后端配置检查

如果前端修改后问题仍然存在，需要检查后端配置：

1. **Django settings.py**：
```python
# Session配置
SESSION_COOKIE_AGE = 86400  # 24小时
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CORS配置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]
```

2. **API权限配置**：
确保 `choice_question/api/exam.py` 中的 `ExamPaperAPI` 类正确处理认证

## 总结

主要问题是API路径配置错误，试卷管理的API应该使用 `/api/plugin/choice/` 路径而不是 `/api/admin/` 路径。通过修正API路径并优化认证处理逻辑，问题应该得到解决。

如果问题仍然存在，请提供：
1. 浏览器控制台的完整错误信息
2. Network标签中失败请求的详细信息
3. 后端Django的日志输出
