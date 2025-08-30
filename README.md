# MetaSpeekOJ - 在线判题系统

## 项目概述

MetaSpeekOJ 是一个基于 Django + Vue.js 的现代化在线判题系统，专注于提供高效、稳定的编程竞赛和教学平台。系统支持多种编程语言，提供完整的题目管理、用户管理、比赛管理等功能。

### 核心特性

- 🚀 **高性能架构**: Django REST Framework + Vue.js 前后端分离
- 📝 **多语言支持**: C/C++, Java, Python, Go 等主流编程语言
- 🎯 **智能判题**: 支持特殊判题、交互式判题等多种判题模式
- 📊 **数据统计**: 完整的提交统计、用户排名、比赛分析
- 🔐 **权限管理**: 细粒度的用户权限控制
- 🎨 **现代化UI**: 响应式设计，支持移动端访问

## 技术栈

### 后端技术
- **框架**: Django 3.2+ / Django REST Framework
- **数据库**: PostgreSQL / MySQL
- **缓存**: Redis
- **消息队列**: Celery
- **容器化**: Docker / Docker Compose

### 前端技术
- **框架**: Vue.js 2.x
- **UI库**: Element UI
- **构建工具**: Webpack
- **状态管理**: Vuex
- **路由**: Vue Router

### 判题系统
- **沙箱**: 自研安全沙箱
- **语言支持**: 多语言编译执行环境
- **资源限制**: 内存、时间、输出限制

## 项目结构

```
MetaSpeekOJ/
├── OnlineJudge/                 # 后端项目
│   ├── account/                 # 用户账户模块
│   ├── announcement/            # 公告模块
│   ├── choice_question/         # 选择题模块 (新增)
│   ├── conf/                    # 系统配置
│   ├── contest/                 # 比赛模块
│   ├── judge/                   # 判题模块
│   ├── problem/                 # 题目模块
│   ├── submission/              # 提交模块
│   ├── utils/                   # 工具模块
│   └── manage.py               # Django 管理脚本
├── OnlineJudgeFE/              # 前端项目
│   ├── src/
│   │   ├── pages/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── store/              # Vuex 状态管理
│   │   └── utils/              # 工具函数
│   └── package.json
└── deploy/                     # 部署配置
```

## 核心功能模块

### 1. 用户管理系统
- 用户注册、登录、权限管理
- 用户资料管理、头像上传
- 管理员后台管理

### 2. 题目管理系统
- 题目创建、编辑、删除
- 题目分类、标签管理
- 测试数据管理
- 题目导入导出

### 3. 选择题模块 (V1.0 新增)
- **前端管理界面**: 现代化的选择题创建和管理界面
- **后端API系统**: RESTful API 支持 CRUD 操作
- **数据模型**: 完整的选择题数据结构
- **难度分级**: 支持简单、中等、困难三个难度等级
- **选项管理**: 支持多选项配置和正确答案设置

### 4. 判题系统
- 多语言编译执行
- 安全沙箱环境
- 实时判题状态
- 详细的错误信息

### 5. 比赛系统
- 比赛创建和管理
- 实时排行榜
- 比赛统计分析

## 开发环境搭建

### 环境要求
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+ / MySQL 8.0+
- Redis 6.0+

### 后端环境搭建

```bash
# 克隆项目
git clone https://github.com/sharelgx/MetaSpeekOJ.git
cd MetaSpeekOJ/OnlineJudge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r deploy/requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端环境搭建

```bash
cd OnlineJudgeFE

# 安装依赖
npm install
# 或使用 yarn
yarn install

# 启动开发服务器
TARGET=http://localhost:8000 NODE_OPTIONS="--openssl-legacy-provider" PORT=8080 npm run dev
```

### 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/onlinejudge

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# 安全配置
SECRET_KEY=your-secret-key
DEBUG=True
```

## API 文档

### 选择题 API

#### 创建选择题
```http
POST /api/admin/choice_question/
Content-Type: application/json

{
  "title": "题目标题",
  "description": "题目描述",
  "difficulty": "easy",
  "options": [
    {"key": "A", "value": "选项A"},
    {"key": "B", "value": "选项B"},
    {"key": "C", "value": "选项C"},
    {"key": "D", "value": "选项D"}
  ],
  "correct_answer": "A"
}
```

#### 获取选择题列表
```http
GET /api/admin/choice_question/?page=1&limit=10&difficulty=easy
```

#### 更新选择题
```http
PUT /api/admin/choice_question/{id}/
Content-Type: application/json

{
  "title": "更新后的标题",
  "difficulty": "medium"
}
```

#### 删除选择题
```http
DELETE /api/admin/choice_question/{id}/
```

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

### 生产环境配置

1. **Nginx 配置**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

2. **Supervisor 配置**
```ini
[program:onlinejudge]
command=/path/to/venv/bin/gunicorn oj.wsgi:application
directory=/path/to/OnlineJudge
user=www-data
autostart=true
autorestart=true
```

## 测试

### 后端测试
```bash
cd OnlineJudge
python manage.py test

# 覆盖率测试
coverage run --source='.' manage.py test
coverage report
```

### 前端测试
```bash
cd OnlineJudgeFE
npm run test
```

## 版本历史

### V1.0 (2025-01-29)
- ✅ 完整的选择题模块实现
- ✅ 现代化管理界面
- ✅ RESTful API 系统
- ✅ 数据验证和错误处理
- ✅ 响应式设计支持
- ✅ 生产环境就绪

### 主要修复
- 🐛 修复选择题难度字段验证错误
- 🐛 修复字体图标加载问题
- 🐛 优化服务端口配置

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 后端遵循 PEP 8 规范
- 前端遵循 ESLint 配置
- 提交信息遵循 Conventional Commits

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址: https://github.com/sharelgx/MetaSpeekOJ
- 问题反馈: https://github.com/sharelgx/MetaSpeekOJ/issues

## 致谢

感谢所有为这个项目做出贡献的开发者们！

---

**MetaSpeekOJ** - 让编程学习更简单，让竞赛更精彩！