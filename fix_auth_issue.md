# 修复试卷管理页面认证问题

## 问题描述
在 http://localhost:8080/admin/exam-papers 页面点击"创建试卷"按钮时，总是重定向到登录页面。

## 问题原因
1. **路由守卫异步问题**：路由守卫中的 `api.getProfile()` 是异步的，可能在组件加载时还未完成
2. **API 认证处理不一致**：`admin/api.js` 和组件中对认证错误的处理不一致
3. **Cookie/Session 问题**：可能存在跨域 Cookie 或 Session 过期问题

## 解决方案

### 方案 1：修复路由守卫（推荐）

修改 `OnlineJudgeFE/src/pages/admin/index.js` 中的路由守卫：

```javascript
// 添加全局路由守卫
router.beforeEach(async (to, from, next) => {
  console.log('Global route guard triggered, target:', to.path, 'name:', to.name)
  
  // 如果访问的是登录页面，直接放行
  if (to.name === 'login') {
    console.log('Accessing login page, allowing access')
    next()
    return
  }
  
  // 检查用户登录状态
  console.log('Checking user profile...')
  try {
    const res = await api.getProfile()
    console.log('Profile API response:', res.data)
    
    if (!res.data.data || !res.data.data.user) {
      // 未登录，重定向到登录页面并携带redirect参数
      console.log('No profile data, redirecting to login with redirect:', to.fullPath)
      next({name: 'login', query: {redirect: to.fullPath}})
    } else {
      // 已登录，更新store并继续
      console.log('Profile data found, updating store and proceeding')
      store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
      
      // 检查是否有管理员权限
      const user = res.data.data.user
      if (user.admin_type !== 'ADMIN' && user.admin_type !== 'SUPER_ADMIN') {
        console.log('User does not have admin privileges')
        Vue.prototype.$error('您没有管理员权限')
        next('/') // 重定向到首页
      } else {
        next()
      }
    }
  } catch (err) {
    // API调用失败，重定向到登录页面
    console.error('Profile API error:', err)
    
    // 清除可能过期的认证信息
    store.dispatch('clearProfile')
    
    next({name: 'login', query: {redirect: to.fullPath}})
  }
})
```

### 方案 2：修复 API 请求配置

修改 `OnlineJudgeFE/src/pages/admin/api.js` 确保正确发送认证信息：

```javascript
// 在文件开头添加请求拦截器
axios.interceptors.request.use(
  config => {
    // 确保发送 cookies
    config.withCredentials = true
    
    // 如果有 token，添加到 header（如果后端支持）
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器统一处理认证错误
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      if (error.response.status === 401 || error.response.status === 403) {
        // 认证失败，清除用户状态并跳转到登录页
        store.dispatch('clearProfile')
        router.push({
          name: 'login',
          query: { redirect: router.currentRoute.fullPath }
        })
      }
    }
    return Promise.reject(error)
  }
)
```

### 方案 3：修复组件中的认证检查

修改 `OnlineJudgeFE/src/pages/admin/views/choice-question/ExamPaperList.vue`：

```javascript
async mounted() {
  console.log('ExamPaperList mounted')
  
  // 确保用户已登录且有权限
  await this.checkAuth()
  
  // 初始化页面数据
  this.init()
},

methods: {
  async checkAuth() {
    try {
      // 如果 store 中没有用户信息，尝试获取
      if (!this.user || !this.user.id) {
        const res = await api.getProfile()
        if (res.data.data && res.data.data.user) {
          this.$store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
        } else {
          throw new Error('No user profile')
        }
      }
      
      // 检查管理员权限
      if (!this.isAdminRole) {
        this.$error('您没有管理员权限')
        this.$router.push('/admin/')
      }
    } catch (err) {
      console.error('Auth check failed:', err)
      this.$router.push({
        name: 'login',
        query: {redirect: this.$route.fullPath}
      })
    }
  },
  
  // 修改 createPaper 方法，添加更好的错误处理
  async createPaper() {
    this.$refs.createForm.validate(async (valid) => {
      if (!valid) return
      
      this.creating = true
      try {
        // 再次检查认证状态
        await this.checkAuth()
        
        const res = await api.createExamPaper(this.createForm)
        this.$message.success('试卷创建成功')
        this.createDialogVisible = false
        await this.loadPapers()
      } catch (err) {
        console.error('创建试卷失败:', err)
        
        // 特殊处理认证错误
        if (err.isAuthError || 
            (err.response && (err.response.status === 401 || err.response.status === 403))) {
          this.$router.push({
            name: 'login',
            query: {redirect: this.$route.fullPath}
          })
        } else {
          this.$message.error('创建试卷失败: ' + (err.message || '未知错误'))
        }
      } finally {
        this.creating = false
      }
    })
  }
}
```

### 方案 4：检查后端配置

确保后端正确配置了 CORS 和 Session：

1. **Django settings.py**：
```python
# Session 配置
SESSION_COOKIE_AGE = 86400  # 24小时
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都更新session
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # 或 'None' 如果是跨域

# CORS 配置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# CSRF 配置
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

2. **检查 API 视图的权限装饰器**：
```python
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

# 确保视图使用了正确的权限类
class ExamPaperViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    # ...
```

## 调试步骤

1. **打开浏览器开发者工具**：
   - 查看 Network 标签页
   - 检查请求的 Headers 中是否包含 Cookie
   - 查看响应状态码

2. **检查 Console 日志**：
   - 查看路由守卫的日志输出
   - 查看 API 调用的日志

3. **验证 Session**：
   - 在浏览器控制台执行：`document.cookie`
   - 检查是否有 sessionid 和 csrftoken

4. **测试 API**：
   ```javascript
   // 在浏览器控制台测试
   fetch('/api/profile', {
     credentials: 'include'
   }).then(r => r.json()).then(console.log)
   ```

## 快速修复

如果需要快速修复，可以：

1. **清除浏览器缓存和 Cookie**
2. **重新登录**
3. **确保使用相同的域名访问**（避免 localhost 和 127.0.0.1 混用）

## 长期解决方案

1. **实现 Token 认证**：使用 JWT 替代 Session
2. **添加认证状态管理**：在 Vuex 中统一管理认证状态
3. **实现自动刷新机制**：定期刷新认证状态
4. **添加请求重试机制**：认证失败时自动重新登录并重试

## 测试验证

修复后，按以下步骤测试：

1. 清除浏览器缓存
2. 访问 `/admin/login` 重新登录
3. 访问 `/admin/exam-papers`
4. 点击"创建试卷"按钮
5. 填写表单并提交
6. 验证是否成功创建

如果问题仍然存在，请检查：
- 后端日志中的认证错误
- 浏览器控制台的错误信息
- Network 标签页中的请求/响应详情
