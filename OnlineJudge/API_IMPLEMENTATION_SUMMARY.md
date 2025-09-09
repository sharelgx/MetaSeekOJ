# 在线评测系统 API 接口实现经验总结

## 项目概述

本项目是一个基于 Django + Vue.js 的在线评测系统，包含传统编程题评测和选择题功能。通过本次开发和调试，积累了丰富的 API 接口实现经验。

## 系统架构

### 后端架构
- **框架**: Django 3.2.13
- **数据库**: PostgreSQL (使用 JSONField)
- **API 设计**: RESTful API
- **认证方式**: Session + CSRF Token
- **端口**: 8086

### 前端架构
- **框架**: Vue.js 2.x
- **HTTP 客户端**: Axios
- **路由**: Vue Router (History 模式)
- **状态管理**: Vuex
- **端口**: 8080 (开发环境)

## API 接口分类与实现经验

### 1. 核心认证 API

#### 已验证的接口
- `GET /api/profile` - 获取用户信息
- `POST /api/login` - 用户登录
- `GET /api/logout` - 用户登出

#### 实现要点
```javascript
// 前端 axios 配置
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.withCredentials = true  // 关键：允许发送 cookie
```

#### 经验总结
1. **CSRF 保护**: Django 默认启用 CSRF 保护，前端必须正确配置 CSRF token
2. **Session 管理**: 使用 `withCredentials: true` 确保 session cookie 正确传递
3. **错误处理**: 统一处理认证失败，自动跳转到登录页面

### 2. 选择题系统 API

#### 已验证的接口
- `GET /api/plugin/choice/questions/` - 获取选择题列表
- `GET /api/plugin/choice/categories/` - 获取题目分类
- `POST /api/plugin/choice/submit/` - 提交选择题答案

#### 实现特点
```python
# Django URL 配置
path('plugin/choice/', include('choice_question.urls')),
```

#### 经验总结
1. **插件化设计**: 选择题作为插件模块，URL 前缀为 `plugin/choice/`
2. **分页支持**: 支持 offset/limit 分页参数
3. **筛选功能**: 支持按分类、标签、难度等多维度筛选

### 3. 统一提交系统 API

#### 已验证的接口
- `GET /api/judge/submissions/` - 获取提交记录
- `POST /api/judge/submit/` - 提交代码
- `GET /api/judge/submission/detail/` - 获取提交详情

#### 实现特点
- 支持多种编程语言
- 实时判题状态更新
- 详细的错误信息反馈

### 4. 管理后台 API

#### 核心接口
- `GET /api/admin/dashboard_info` - 仪表板信息
- `GET /api/admin/choice_question` - 选择题管理
- `GET /api/admin/announcement` - 公告管理

## 前端 API 调用最佳实践

### 1. 统一的 Ajax 封装

```javascript
function ajax(url, method, options) {
  if (options !== undefined) {
    var {params = {}, data = {}} = options
  } else {
    params = data = {}
  }
  
  return new Promise((resolve, reject) => {
    axios({
      url,
      method,
      params,
      data,
      timeout: 30000,
      withCredentials: true
    }).then(res => {
      // 统一的响应处理
      if (res.data.error !== null) {
        // 错误处理
        if (res.data.data && res.data.data.startsWith('Please login')) {
          // 处理登录过期
          const authError = new Error('Authentication required')
          authError.isAuthError = true
          reject(authError)
        } else {
          reject(res)
        }
      } else {
        resolve(res)
      }
    }, res => {
      // 网络错误处理
      reject(res)
    })
  })
}
```

### 2. API 方法映射

创建了 `api-mapping.js` 统一管理 API 方法名称：

```javascript
export const API_MAPPING = {
  categories: {
    list: 'getChoiceQuestionCategories',
    create: 'createChoiceQuestionCategory'
  },
  choiceQuestions: {
    list: 'getChoiceQuestions',
    submit: 'submitChoiceQuestion'
  }
}
```

### 3. API 调用验证

开发了 `api-validator.js` 在开发环境检查 API 调用一致性：

```javascript
class ApiValidator {
  validateCall(methodName, filePath = 'unknown') {
    // 检查废弃的 API
    // 检查无效的 API 方法
    // 提供建议的 API 方法
  }
}
```

## 路由守卫实现经验

### 全局路由守卫设计

```javascript
// 管理后台路由守卫
router.beforeEach((to, from, next) => {
  console.log('Global route guard triggered, target:', to.path)
  
  // 登录页面直接放行
  if (to.name === 'login') {
    next()
    return
  }
  
  // 检查用户登录状态
  api.getProfile().then(res => {
    if (!res.data.data) {
      // 未登录，重定向到登录页面并携带 redirect 参数
      next({name: 'login', query: {redirect: to.fullPath}})
    } else {
      // 已登录，更新 store 并继续
      store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
      next()
    }
  }).catch(err => {
    // API 调用失败，重定向到登录页面
    next({name: 'login', query: {redirect: to.fullPath}})
  })
})
```

### 普通用户端路由守卫

```javascript
// OJ 路由守卫
router.beforeEach((to, from, next) => {
  Vue.prototype.$Loading.start()
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!storage.get(STORAGE_KEY.AUTHED)) {
      Vue.prototype.$error('Please login first')
      store.commit(types.CHANGE_MODAL_STATUS, {mode: 'login', visible: true})
      next({name: 'home'})
    } else {
      next()
    }
  } else {
    next()
  }
})
```

## 常见问题与解决方案

### 1. CORS 和 withCredentials 问题

**问题**: 前端无法发送 cookie，导致 session 认证失败

**解决方案**:
```javascript
// 前端配置
axios.defaults.withCredentials = true

// 后端 Django 配置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['http://localhost:8080']
```

### 2. CSRF Token 处理

**问题**: POST 请求被 CSRF 保护拦截

**解决方案**:
```javascript
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'
```

### 3. 路由重定向循环

**问题**: 登录检查失败时出现无限重定向

**解决方案**:
- 登录页面必须在路由守卫中特殊处理
- 使用 `query.redirect` 参数保存原始访问路径
- API 错误时统一处理，避免重复重定向

### 4. Node.js 版本兼容性

**问题**: `Error: error:0308010C:digital envelope routines::unsupported`

**解决方案**:
```bash
NODE_OPTIONS="--openssl-legacy-provider" npm run build
NODE_OPTIONS="--openssl-legacy-provider" npm run dev
```

## API 接口状态总结

### ✅ 正常工作的接口
1. **认证相关**: `/api/profile`, `/api/login`, `/api/logout`
2. **选择题系统**: `/api/plugin/choice/questions/`, `/api/plugin/choice/categories/`
3. **管理后台**: `/api/admin/dashboard_info`, `/api/admin/choice_question`
4. **网站配置**: `/api/website`

### ⚠️ 需要认证的接口
1. **统一提交系统**: `/api/judge/submissions/` (需要用户登录)
2. **用户相关**: `/api/profile` (未登录时返回 null)
3. **管理功能**: 所有 `/api/admin/` 接口需要管理员权限

### 🔧 需要进一步优化的接口
1. **错误处理**: 统一错误码和错误信息格式
2. **API 文档**: 完善 API 文档和参数说明
3. **性能优化**: 添加缓存机制和分页优化

## 开发建议

### 1. API 设计原则
- 遵循 RESTful 设计规范
- 统一的响应格式: `{error: null|string, data: any}`
- 合理的 HTTP 状态码使用
- 详细的错误信息提供

### 2. 前端开发建议
- 使用统一的 API 调用封装
- 实现 API 方法名映射和验证
- 完善的错误处理和用户提示
- 合理的加载状态管理

### 3. 安全考虑
- 启用 CSRF 保护
- 合理的 CORS 配置
- Session 安全设置
- 输入验证和 SQL 注入防护

### 4. 性能优化
- API 响应缓存
- 分页和懒加载
- 请求去重和防抖
- 合理的超时设置

## 总结

通过本次项目开发，我们成功实现了一个功能完整的在线评测系统，包含了传统编程题评测和选择题功能。在 API 接口实现过程中，我们解决了认证、CORS、路由守卫等多个关键问题，积累了宝贵的开发经验。

这些经验和最佳实践为后续的项目开发提供了重要参考，特别是在前后端分离架构下的 API 设计和实现方面。