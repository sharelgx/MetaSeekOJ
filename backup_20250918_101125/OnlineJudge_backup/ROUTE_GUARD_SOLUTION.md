# 全局路由守卫和重定向问题解决方案

## 问题背景

在开发在线评测系统的过程中，我们遇到了全局路由守卫和重定向相关的问题。主要表现为：

1. 用户访问需要认证的页面时，未正确重定向到登录页面
2. 登录状态检查逻辑不完善，导致用户体验不佳
3. 前后端认证状态不同步
4. 重定向循环问题

## 问题分析

### 1. 原始问题现象

```
浏览器日志显示：
- 访问 http://localhost:8080/admin/exam-papers
- 全局路由守卫触发，检查用户profile
- GET profile请求成功但数据为空（响应为 {error: null, data: null}）
- 重定向到登录页并携带 redirect 参数
- 访问登录页时允许访问
```

### 2. 根本原因分析

1. **认证状态检查不准确**: `api.getProfile()` 返回 `{error: null, data: null}` 表示用户未登录
2. **withCredentials 配置缺失**: 前端请求未携带认证 cookie
3. **路由守卫逻辑不完善**: 未正确处理 API 调用失败的情况
4. **重定向参数处理**: 需要保存用户原始访问路径

## 解决方案详解

### 1. 前端 Axios 配置修复

#### 问题代码
```javascript
// 原始配置缺少 withCredentials
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'
```

#### 修复后的配置
```javascript
// /src/pages/admin/api.js
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.withCredentials = true  // 关键修复：允许发送cookie
```

#### 修复说明
- `withCredentials: true` 确保跨域请求时发送认证 cookie
- 这是解决认证问题的关键配置
- 必须与后端 CORS 配置配合使用

### 2. 全局路由守卫优化

#### 管理后台路由守卫实现

```javascript
// /src/pages/admin/index.js
router.beforeEach((to, from, next) => {
  console.log('Global route guard triggered, target:', to.path, 'name:', to.name)
  
  // 如果访问的是登录页面，直接放行
  if (to.name === 'login') {
    console.log('Accessing login page, allowing access')
    next()
    return
  }
  
  // 检查用户登录状态
  console.log('Checking user profile...')
  api.getProfile().then(res => {
    console.log('Profile API response:', res.data)
    if (!res.data.data) {
      // 未登录，重定向到登录页面并携带redirect参数
      console.log('No profile data, redirecting to login with redirect:', to.fullPath)
      next({name: 'login', query: {redirect: to.fullPath}})
    } else {
      // 已登录，更新store并继续
      console.log('Profile data found, updating store and proceeding')
      store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
      next()
    }
  }).catch(err => {
    // API调用失败，重定向到登录页面
    console.error('Profile API error:', err)
    next({name: 'login', query: {redirect: to.fullPath}})
  })
})
```

#### 普通用户端路由守卫实现

```javascript
// /src/pages/oj/router/index.js
router.beforeEach((to, from, next) => {
  Vue.prototype.$Loading.start()
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!storage.get(STORAGE_KEY.AUTHED)) {
      Vue.prototype.$error('Please login first')
      store.commit(types.CHANGE_MODAL_STATUS, {mode: 'login', visible: true})
      next({
        name: 'home'
      })
    } else {
      next()
    }
  } else {
    next()
  }
})
```

### 3. API 错误处理优化

#### 统一的 Ajax 封装

```javascript
function ajax(url, method, options) {
  if (options !== undefined) {
    var {params = {}, data = {}} = options
  } else {
    params = data = {}
  }
  
  console.log(`API: ${method.toUpperCase()} ${url}`, {params, data})
  
  return new Promise((resolve, reject) => {
    axios({
      url,
      method,
      params,
      data,
      timeout: 30000, // 增加超时时间到30秒
      withCredentials: true // 允许发送cookie
    }).then(res => {
      console.log(`API: ${method.toUpperCase()} ${url} - Success:`, res.data)
      
      // API正常返回(status=20x), 是否错误通过有无error判断
      if (res.data.error !== null) {
        console.error(`API: ${method.toUpperCase()} ${url} - Error:`, res.data.data)
        
        // 检查是否是登录相关错误
        if (res.data.data && typeof res.data.data === 'string' && 
            res.data.data.startsWith('Please login')) {
          console.log('API: Authentication error detected')
          // 不在这里直接跳转，而是抛出特殊错误让组件处理
          const authError = new Error('Authentication required')
          authError.isAuthError = true
          authError.originalData = res.data.data
          reject(authError)
        } else {
          reject(res)
        }
      } else {
        resolve(res)
      }
    }, res => {
      // API请求异常，一般为Server error 或 network error
      console.error(`API: ${method.toUpperCase()} ${url} - Network Error:`, res)
      reject(res)
    })
  })
}
```

### 4. 后端 CORS 配置

#### Django 设置

```python
# settings.py
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 或者在开发环境使用
CORS_ALLOW_ALL_ORIGINS = True  # 仅开发环境
CORS_ALLOW_CREDENTIALS = True
```

## 实施步骤

### 第一步：修复前端 Axios 配置

1. 在 `/src/pages/admin/api.js` 中添加 `withCredentials: true`
2. 在 `/src/pages/oj/api.js` 中添加相同配置
3. 确保所有 API 调用都使用统一的 ajax 函数

### 第二步：优化路由守卫逻辑

1. 完善登录页面的特殊处理逻辑
2. 添加详细的调试日志
3. 实现 redirect 参数的正确传递和处理
4. 添加 API 调用失败的容错处理

### 第三步：测试验证

1. 测试未登录用户访问受保护页面
2. 测试登录后的正常访问
3. 测试登录后重定向到原始页面
4. 测试 API 调用失败的处理

## 测试用例

### 1. 未登录用户访问管理后台

**测试步骤**:
1. 清除浏览器 cookie
2. 访问 `http://localhost:8080/admin/exam-papers`
3. 观察重定向行为

**期望结果**:
- 自动重定向到 `http://localhost:8080/admin/login?redirect=/admin/exam-papers`
- 控制台显示相关调试信息
- 不出现无限重定向

### 2. 登录后访问原始页面

**测试步骤**:
1. 在登录页面输入正确的用户名密码
2. 点击登录
3. 观察登录后的跳转

**期望结果**:
- 登录成功后自动跳转到 `/admin/exam-papers`
- 页面正常显示
- 用户状态正确更新

### 3. API 认证状态检查

**测试步骤**:
1. 使用浏览器开发者工具查看网络请求
2. 观察 `/api/profile` 请求的 cookie 发送情况
3. 检查响应数据

**期望结果**:
- 请求头包含 cookie 信息
- 响应数据符合预期格式
- 认证状态正确反映

## 常见问题排查

### 1. 仍然出现认证失败

**可能原因**:
- 后端 CORS 配置不正确
- Session 配置问题
- Cookie 域名或路径设置问题

**排查方法**:
```bash
# 检查 cookie 是否正确发送
curl -X GET http://localhost:8086/api/profile -H "Content-Type: application/json" -v --cookie-jar cookies.txt

# 先登录获取 cookie
curl -X POST http://localhost:8086/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}' -v --cookie-jar cookies.txt

# 使用 cookie 访问 profile
curl -X GET http://localhost:8086/api/profile -H "Content-Type: application/json" -v --cookie cookies.txt
```

### 2. 重定向循环问题

**可能原因**:
- 登录页面也被路由守卫拦截
- redirect 参数处理逻辑错误
- API 调用在路由守卫中出现异常

**解决方法**:
- 确保登录页面在路由守卫中被正确排除
- 添加更多调试日志定位问题
- 检查 API 调用的错误处理逻辑

### 3. 开发环境 vs 生产环境

**注意事项**:
- 开发环境可以使用 `CORS_ALLOW_ALL_ORIGINS = True`
- 生产环境必须明确指定允许的域名
- Cookie 的 secure 和 samesite 设置在不同环境下的表现

## 最佳实践总结

### 1. 前端最佳实践

- **统一配置**: 所有 API 调用使用统一的 axios 配置
- **错误处理**: 实现统一的错误处理和用户提示
- **状态管理**: 正确维护用户登录状态
- **调试信息**: 在开发环境提供详细的调试日志

### 2. 路由守卫最佳实践

- **特殊页面处理**: 登录页面等特殊页面需要特殊处理
- **重定向参数**: 正确保存和恢复用户原始访问路径
- **容错处理**: API 调用失败时的合理降级处理
- **性能考虑**: 避免不必要的 API 调用

### 3. 后端最佳实践

- **CORS 配置**: 正确配置跨域和认证相关设置
- **Session 管理**: 合理的 session 超时和清理机制
- **错误响应**: 统一的错误响应格式
- **安全考虑**: 适当的 CSRF 保护和输入验证

## 总结

通过以上解决方案，我们成功解决了全局路由守卫和重定向相关的问题。关键的修复点包括：

1. **添加 `withCredentials: true` 配置**，确保认证 cookie 正确发送
2. **完善路由守卫逻辑**，正确处理登录检查和重定向
3. **优化错误处理**，提供更好的用户体验
4. **添加详细调试信息**，便于问题排查

这些解决方案不仅解决了当前的问题，也为后续的开发提供了可靠的基础架构。通过合理的测试和验证，确保了系统的稳定性和用户体验。