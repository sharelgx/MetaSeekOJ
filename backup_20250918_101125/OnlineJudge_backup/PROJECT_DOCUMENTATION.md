# 在线评测系统项目文档

## 项目概述

本项目是一个功能完整的在线评测系统，支持传统编程题评测和选择题功能。系统采用前后端分离架构，后端使用 Django，前端使用 Vue.js。

### 技术栈

**后端技术栈**:
- Django 3.2.13
- PostgreSQL 数据库
- Django REST Framework
- CORS 支持
- Session 认证

**前端技术栈**:
- Vue.js 2.x
- Vue Router (History 模式)
- Vuex 状态管理
- Axios HTTP 客户端
- Element UI 组件库

### 项目结构

```
OnlineJudge/                    # 后端项目根目录
├── manage.py                   # Django 管理脚本
├── oj/                        # 主应用
│   ├── urls.py               # 主路由配置
│   └── settings.py           # Django 设置
├── choice_question/           # 选择题插件
├── judge/                     # 统一提交系统
├── API_IMPLEMENTATION_SUMMARY.md    # API 实现经验总结
├── ROUTE_GUARD_SOLUTION.md          # 路由守卫解决方案
└── PROJECT_DOCUMENTATION.md         # 项目主文档

OnlineJudgeFE/                 # 前端项目根目录
├── src/
│   ├── pages/
│   │   ├── admin/            # 管理后台
│   │   └── oj/               # 普通用户端
│   ├── utils/                # 工具函数
│   └── store/                # Vuex 状态管理
└── package.json              # 前端依赖配置
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+ (建议使用 Node.js 16)
- PostgreSQL 12+

### 后端启动

```bash
# 进入后端目录
cd OnlineJudge

# 激活虚拟环境
source django_env/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver 0.0.0.0:8086
```

### 前端启动

```bash
# 进入前端目录
cd OnlineJudgeFE

# 安装依赖
npm install

# 启动开发服务器（解决 Node.js 版本兼容性问题）
NODE_OPTIONS="--openssl-legacy-provider" npm run dev
```

### 构建生产版本

```bash
# 前端构建
NODE_OPTIONS="--openssl-legacy-provider" npm run build
```

## 核心功能模块

### 1. 用户认证系统

- **登录/登出**: 基于 Session 的用户认证
- **权限管理**: 普通用户和管理员权限分离
- **全局路由守卫**: 自动检查用户登录状态

### 2. 选择题系统

- **题目管理**: 支持单选题和多选题
- **分类标签**: 题目分类和标签管理
- **在线答题**: 实时提交和结果反馈
- **统计分析**: 答题统计和正确率分析

### 3. 编程题评测

- **多语言支持**: 支持多种编程语言
- **实时判题**: 在线代码提交和评测
- **结果展示**: 详细的评测结果和错误信息

### 4. 管理后台

- **题目管理**: 编程题和选择题的增删改查
- **用户管理**: 用户信息和权限管理
- **系统配置**: 网站配置和公告管理
- **数据统计**: 各类统计报表和分析

## 重要技术实现

### API 接口设计

详细的 API 接口实现经验请参考：[API_IMPLEMENTATION_SUMMARY.md](./API_IMPLEMENTATION_SUMMARY.md)

**核心 API 接口**:
- `/api/profile` - 用户信息获取
- `/api/login` - 用户登录
- `/api/plugin/choice/questions/` - 选择题列表
- `/api/judge/submissions/` - 提交记录
- `/api/admin/*` - 管理后台接口

### 路由守卫实现

详细的路由守卫解决方案请参考：[ROUTE_GUARD_SOLUTION.md](./ROUTE_GUARD_SOLUTION.md)

**关键配置**:
```javascript
// 前端 Axios 配置
axios.defaults.withCredentials = true
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'
```

## 已解决的关键问题

### 1. 认证和跨域问题

**问题**: 前端无法发送认证 cookie，导致用户登录状态丢失

**解决方案**:
- 前端配置 `axios.defaults.withCredentials = true`
- 后端配置 `CORS_ALLOW_CREDENTIALS = True`
- 正确设置 CSRF Token 处理

### 2. 路由守卫和重定向

**问题**: 用户访问受保护页面时重定向逻辑不正确

**解决方案**:
- 实现完善的全局路由守卫
- 正确处理登录页面的特殊逻辑
- 保存和恢复用户原始访问路径

### 3. Node.js 版本兼容性

**问题**: `Error: error:0308010C:digital envelope routines::unsupported`

**解决方案**:
```bash
NODE_OPTIONS="--openssl-legacy-provider" npm run dev
NODE_OPTIONS="--openssl-legacy-provider" npm run build
```

## API 接口状态

### ✅ 正常工作的接口

1. **认证相关**
   - `GET /api/profile` - 获取用户信息
   - `POST /api/login` - 用户登录
   - `GET /api/logout` - 用户登出

2. **选择题系统**
   - `GET /api/plugin/choice/questions/` - 获取选择题列表
   - `GET /api/plugin/choice/categories/` - 获取题目分类
   - `POST /api/plugin/choice/submit/` - 提交选择题答案

3. **管理后台**
   - `GET /api/admin/dashboard_info` - 仪表板信息
   - `GET /api/admin/choice_question` - 选择题管理
   - `GET /api/admin/announcement` - 公告管理

4. **网站配置**
   - `GET /api/website` - 网站配置信息

### ⚠️ 需要认证的接口

1. **统一提交系统**
   - `GET /api/judge/submissions/` - 需要用户登录
   - `POST /api/judge/submit/` - 需要用户登录

2. **用户相关**
   - `GET /api/profile` - 未登录时返回 null

3. **管理功能**
   - 所有 `/api/admin/` 接口需要管理员权限

## 开发规范

### 前端开发规范

1. **API 调用**
   - 使用统一的 ajax 函数封装
   - 实现统一的错误处理
   - 添加适当的加载状态

2. **路由配置**
   - 合理使用 `meta.requiresAuth` 标记需要认证的路由
   - 实现完善的路由守卫逻辑

3. **状态管理**
   - 使用 Vuex 管理全局状态
   - 正确维护用户登录状态

### 后端开发规范

1. **API 设计**
   - 遵循 RESTful 设计原则
   - 统一的响应格式: `{error: null|string, data: any}`
   - 合理的 HTTP 状态码使用

2. **安全考虑**
   - 启用 CSRF 保护
   - 合理的 CORS 配置
   - 输入验证和 SQL 注入防护

## 部署指南

### 开发环境部署

1. **后端服务**
   ```bash
   python manage.py runserver 0.0.0.0:8086
   ```

2. **前端服务**
   ```bash
   NODE_OPTIONS="--openssl-legacy-provider" npm run dev
   ```

3. **访问地址**
   - 前端: http://localhost:8080
   - 后端 API: http://localhost:8086/api
   - 管理后台: http://localhost:8080/admin

### 生产环境部署

1. **前端构建**
   ```bash
   NODE_OPTIONS="--openssl-legacy-provider" npm run build
   ```

2. **后端配置**
   - 配置生产数据库
   - 设置正确的 CORS 域名
   - 配置静态文件服务

3. **Web 服务器配置**
   - 使用 Nginx 作为反向代理
   - 配置 HTTPS 证书
   - 设置适当的缓存策略

## 测试指南

### API 接口测试

```bash
# 测试用户信息接口
curl -X GET http://localhost:8086/api/profile -H "Content-Type: application/json" -v

# 测试选择题列表接口
curl -X GET http://localhost:8086/api/plugin/choice/questions/ -H "Content-Type: application/json" -v

# 测试登录接口
curl -X POST http://localhost:8086/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}' -v
```

### 前端功能测试

1. **路由守卫测试**
   - 清除浏览器 cookie
   - 访问需要认证的页面
   - 验证重定向到登录页面

2. **API 调用测试**
   - 检查网络请求是否携带 cookie
   - 验证 CSRF Token 是否正确发送
   - 测试错误处理逻辑

## 故障排查

### 常见问题

1. **认证失败**
   - 检查 `withCredentials` 配置
   - 验证 CORS 设置
   - 确认 cookie 域名和路径

2. **重定向循环**
   - 检查登录页面是否被路由守卫拦截
   - 验证 redirect 参数处理逻辑
   - 查看 API 调用的错误处理

3. **构建失败**
   - 使用 `NODE_OPTIONS="--openssl-legacy-provider"`
   - 检查 Node.js 版本兼容性
   - 清除 node_modules 重新安装

### 调试技巧

1. **前端调试**
   - 使用浏览器开发者工具查看网络请求
   - 检查 Console 中的错误信息
   - 使用 Vue DevTools 查看组件状态

2. **后端调试**
   - 查看 Django 开发服务器日志
   - 使用 Django Debug Toolbar
   - 检查数据库查询和性能

## 未来改进计划

### 功能增强

1. **用户体验优化**
   - 实现更好的加载状态提示
   - 添加离线支持
   - 优化移动端适配

2. **性能优化**
   - 实现 API 响应缓存
   - 添加 CDN 支持
   - 优化数据库查询

3. **功能扩展**
   - 添加更多编程语言支持
   - 实现实时协作功能
   - 添加代码审查功能

### 技术升级

1. **前端技术栈**
   - 考虑升级到 Vue 3
   - 使用 TypeScript
   - 采用现代化的构建工具

2. **后端技术栈**
   - 升级到最新版本的 Django
   - 考虑使用 Django REST Framework
   - 实现 API 版本管理

## 贡献指南

### 开发流程

1. Fork 项目到个人仓库
2. 创建功能分支
3. 完成开发和测试
4. 提交 Pull Request
5. 代码审查和合并

### 代码规范

1. **Python 代码**
   - 遵循 PEP 8 规范
   - 使用有意义的变量和函数名
   - 添加适当的注释和文档

2. **JavaScript 代码**
   - 使用 ESLint 检查代码质量
   - 遵循 Vue.js 官方风格指南
   - 保持代码简洁和可读性

## 联系信息

如有问题或建议，请通过以下方式联系：

- 项目仓库: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 技术讨论: [Discussion Forum]

---

**最后更新**: 2025年9月8日
**文档版本**: v1.0
**项目状态**: 开发中