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
MetaSeekOJ/
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
git clone https://github.com/sharelgx/MetaSeekOJ.git
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

## 选择题模块架构调研报告

### 模块集成深度分析

#### 1. 当前架构状态
选择题模块目前采用**深度集成**架构，作为 Django 应用完全集成在主项目中：

- **后端集成**：注册在 `oj/settings.py` 的 `LOCAL_APPS` 中
- **URL路由**：通过 `oj/urls.py` 集成 API 路由（`api/plugin/choice/` 和 `api/admin/`）
- **数据库**：与主项目共享数据库，已完成迁移集成
- **前端集成**：路由和组件直接集成在主前端项目中

#### 2. 项目结构对比

**当前集成结构**：
```
OnlineJudge/choice_question/     # 集成版本（当前运行）
├── models/                      # 数据模型
├── views.py                     # API视图
├── urls.py                      # URL配置
└── admin_urls.py               # 管理端URL

qduoj-choice-question-plugin/    # 独立插件版本（备份/参考）
├── backend/                     # 独立后端
├── frontend/                    # 独立前端
└── install.sh                  # 安装脚本
```

#### 3. 独立化复杂度评估

**如果将选择题模块独立化，需要进行以下修改**：

##### 后端修改（高复杂度）
- 从 `settings.py` 移除 `choice_question` 应用注册
- 修改 `urls.py` 移除相关路由配置
- 重构为独立 Django 项目，配置独立的设置文件
- 处理数据库迁移和数据分离
- 实现服务间通信机制（API调用或消息队列）
- 处理用户认证和权限同步问题

##### 前端修改（中等复杂度）
- 修改 API baseURL 配置（当前硬编码为 `/api`）
- 重新配置路由系统，处理跨域问题
- 修改组件导入路径和依赖关系
- 可能需要独立的前端构建和部署流程
- 处理用户会话和认证状态同步

##### 运维复杂度（高复杂度）
- 需要独立的服务部署和监控
- 数据库连接和备份策略调整
- 负载均衡和服务发现配置
- 日志聚合和错误追踪

#### 4. 架构建议

**推荐保持当前集成架构**，原因如下：

1. **开发效率**：集成架构便于开发、调试和维护
2. **部署简单**：单一应用部署，减少运维复杂度
3. **性能优势**：避免服务间通信开销
4. **数据一致性**：共享数据库，事务处理更简单
5. **用户体验**：统一的前端界面和用户会话

**适合独立化的场景**：
- 需要独立扩展选择题服务
- 多个 OJ 系统共享选择题模块
- 团队分工需要独立开发和部署

### 技术债务分析

#### 当前技术债务
- 前端 API 配置硬编码（`baseURL = '/api'`）
- 路由配置耦合度较高
- 缺少服务边界抽象

#### 改进建议
- 引入配置管理，支持环境变量配置 API 地址
- 抽象服务接口，为未来可能的独立化做准备
- 完善模块间的依赖管理

## 选择题分类标签功能调研报告

### 调研概述

本次调研旨在检查选择题模块的分类和标签功能是否已开发但未完全集成到系统中。通过对代码库的全面分析，发现该功能已在后端完全实现，但前端管理界面存在缺失。

### 后端实现状况

#### ✅ 已完全实现

**数据模型**：
- `Category` 模型：使用 django-mptt 实现树形分类结构
  - 支持父子分类关系
  - 包含名称、描述、排序、启用状态等字段
  - 自动维护题目数量统计

- `QuestionTag` 模型：完整的标签系统
  - 支持多种标签类型（难度、学科、知识点、自定义）
  - 包含颜色、描述、启用状态等字段
  - 自动维护关联题目数量

- `ChoiceQuestion` 模型：已集成分类和标签关联
  - `category` 字段：外键关联分类
  - `tags` 字段：多对多关联标签

**API 接口**：
- 管理端 API（`admin_views.py`）：
  - `ChoiceQuestionCategoryAdminAPI`：分类的增删改查
  - `ChoiceQuestionTagAdminAPI`：标签的增删改查
  - `ChoiceQuestionAdminAPI`：支持按分类和标签筛选

- 用户端 API（`views.py`）：
  - `ChoiceQuestionCategoryAPI`：获取分类列表
  - `ChoiceQuestionTagAPI`：获取标签列表
  - `ChoiceQuestionAPI`：支持按分类和标签筛选

**数据库支持**：
- 迁移文件 `0001_initial.py` 已包含所有相关表结构
- 数据库层面完全支持分类和标签功能

### 前端实现状况

#### ✅ 用户端已实现
- `ChoiceQuestionDetail.vue`：展示题目的分类和标签信息
- `ChoiceQuestionList.vue`：提供分类和标签筛选功能
- `WrongQuestionBook.vue`：支持按分类和标签筛选错题
- API 调用：已集成获取分类和标签列表的接口

#### ❌ 管理端缺失
- **路由配置**：管理端路由中无分类和标签管理页面
- **管理界面**：缺少分类和标签的创建、编辑、删除界面
- **功能入口**：管理后台无分类和标签管理的导航入口

### 集成状态评估

| 功能模块 | 后端实现 | 前端用户端 | 前端管理端 | 集成状态 |
|---------|---------|-----------|-----------|----------|
| 数据模型 | ✅ 完整 | - | - | 已集成 |
| API 接口 | ✅ 完整 | ✅ 完整 | ❌ 缺失界面 | 部分集成 |
| 用户筛选 | ✅ 支持 | ✅ 完整 | - | 已集成 |
| 管理功能 | ✅ 完整 | - | ❌ 缺失界面 | 未集成 |

### 问题分析

#### 核心问题
选择题分类和标签功能在技术层面已完全开发完成，但**管理端前端界面缺失**，导致管理员无法通过 Web 界面管理分类和标签。

#### 具体缺失
1. **管理页面**：无分类和标签的管理界面组件
2. **路由配置**：管理端路由未包含相关页面路径
3. **导航菜单**：管理后台侧边栏无相关功能入口
4. **权限控制**：缺少管理权限的前端验证

### 完善建议

#### 短期目标（1-2 天）
1. **创建管理页面**：
   - `CategoryManagement.vue`：分类管理界面
   - `TagManagement.vue`：标签管理界面

2. **配置路由**：
   - 在 `admin/router.js` 中添加相关路由
   - 配置页面访问权限

3. **添加导航**：
   - 在管理后台侧边栏添加功能入口
   - 设计合理的菜单层级

#### 中期目标（3-5 天）
1. **功能增强**：
   - 批量操作（批量删除、批量启用/禁用）
   - 分类树形拖拽排序
   - 标签颜色选择器

2. **用户体验**：
   - 搜索和过滤功能
   - 数据统计和可视化
   - 操作确认和提示

### 结论

选择题的分类和标签功能**已在后端完全开发完成**，用户端前端也已集成，但**管理端前端界面缺失**。这是一个典型的"功能已开发但未完全集成"的情况。

**建议优先级**：高 - 该功能对提升系统管理效率具有重要意义，且技术实现成本较低，主要是前端界面开发工作。

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