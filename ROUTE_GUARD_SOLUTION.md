# 路由守卫问题解决方案

## 问题分析

通过深入调试发现，路由守卫问题的根本原因是：

1. **SessionManagementAPI权限检查**：`/api/sessions`接口使用了`@login_required`装饰器
2. **错误响应格式**：Django后端返回`{"error": "permission-denied", "data": "Please login first"}`而不是HTTP 401状态码
3. **前端错误处理缺失**：store中的`getProfile`方法没有错误处理，导致Promise被静默忽略
4. **路由守卫逻辑**：当API调用失败时，路由守卫无法正确捕获错误

## 解决方案

### 方案1：修复前端store错误处理（推荐）

修改`/home/metaspeekoj/OnlineJudgeFE/src/store/modules/user.js`中的`getProfile`方法：

```javascript
const actions = {
  getProfile ({commit}) {
    return api.getUserInfo().then(res => {
      commit(types.CHANGE_PROFILE, {
        profile: res.data.data || {}
      })
      return res
    }).catch(err => {
      // 清除可能过期的认证信息
      commit(types.CHANGE_PROFILE, {
        profile: {}
      })
      // 重新抛出错误，让调用者处理
      throw err
    })
  },
  // ... 其他方法
}
```

### 方案2：修改后端API响应格式

修改`/home/metaspeekoj/OnlineJudge/account/decorators.py`中的`login_required`装饰器：

```python
class login_required(BasePermissionDecorator):
    def check_permission(self):
        return self.request.user.is_authenticated
    
    def __call__(self, *args, **kwargs):
        self.request = args[1]
        
        if self.check_permission():
            if self.request.user.is_disabled:
                return self.error("Your account is disabled")
            return self.func(*args, **kwargs)
        else:
            # 返回HTTP 401状态码而不是JSON错误
            from django.http import JsonResponse
            return JsonResponse(
                {"error": "permission-denied", "data": "Please login first"}, 
                status=401
            )
```

### 方案3：移除SessionManagementAPI的权限检查

如果sessions接口不需要严格的权限检查，可以移除`@login_required`装饰器：

```python
class SessionManagementAPI(APIView):
    # @login_required  # 移除这行
    def get(self, request):
        # 在方法内部检查认证状态
        if not request.user.is_authenticated:
            return self.error("Please login first")
        # ... 其余代码保持不变
```

## 推荐实施步骤

1. **立即修复**：采用方案1修复前端store错误处理
2. **长期优化**：考虑采用方案2统一后端错误响应格式
3. **测试验证**：确保修复后路由守卫正常工作

## 测试验证

修复后需要测试以下场景：
1. 未登录用户直接访问创建试卷页面
2. 已登录用户访问创建试卷页面
3. 登录状态过期时的处理
4. 权限不足时的处理