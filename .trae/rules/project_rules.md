# 用中文和我交流
# MetaSeekOJ 项目运行目录配置

## 项目基本信息

- **项目名称**: MetaSeekOJ (在线判题系统)
- **项目类型**: 前后端分离的Web应用
- **技术栈**: Django (后端) + Vue.js (前端)
- **工作目录**: `/home/metaspeekoj`

## 项目结构说明

**项目核心目录**：
- **前端核心**: `/home/metaspeekoj/OnlineJudgeFE/` - Vue.js前端应用
- **后端核心**: `/home/metaspeekoj/OnlineJudge/` - Django后端服务

### 后端服务 (OnlineJudge) - 项目核心
- **目录**: `/home/metaspeekoj/OnlineJudge`
- **服务**: Django 后端服务
- **端口**: 8086
- **访问地址**: http://localhost:8086
- **管理后台**: http://localhost:8086/admin/login/
- **启动命令**: `cd /home/metaspeekoj/OnlineJudge && source django_env/bin/activate && python manage.py runserver 0.0.0.0:8086`
- **虚拟环境**: django_env
- **当前状态**: 运行中 (Command ID: f49defab-0b81-4dde-a172-3b0e5d682ca5)

### 前端服务 (OnlineJudgeFE) - 项目核心
- **目录**: `/home/metaspeekoj/OnlineJudgeFE`
- **服务**: Webpack开发服务器
- **端口**: 8080
- **访问地址**: http://localhost:8080
- **管理界面**: http://localhost:8080/admin/choice-questions
- **启动命令**: `cd /home/metaspeekoj/OnlineJudgeFE && npx webpack-dev-server --config webpack.dev.js`
- **当前状态**: 运行中 (Command ID: 9f319c24-1e2a-437b-927c-75ddf56b712a)

## 主要功能模块

### 后端功能
- 用户认证与权限管理
- 题目管理系统
- 选择题管理 (支持批量导入)
- 在线判题服务
- 比赛管理
- 数据统计与分析

### 前端功能
- 用户界面 (题目浏览、提交代码)
- 管理后台 (题目管理、用户管理)
- 选择题管理界面
- 比赛界面
- 数据可视化

## 重要文件和目录

### 后端重要文件
- `manage.py`: Django管理脚本
- `oj/settings.py`: 项目配置文件
- `account/`: 用户账户模块
- `problem/`: 题目管理模块
- `contest/`: 比赛管理模块
- `judge/`: 判题服务模块
- `django_env/`: Python虚拟环境

### 前端重要文件
- `webpack.dev.js`: Webpack开发配置
- `src/pages/admin/`: 管理后台页面
- `src/i18n/`: 国际化配置
- `src/store/`: Vuex状态管理
- `src/utils/`: 工具函数

## 外部数据存储 (非项目核心文件)

### 题目数据 (外部存储)
- **位置**: `/home/metaspeekoj/data/`
- **说明**: 外部题目数据存储，非项目核心文件
- **分类**: level1, level2, level3, level4, level5, cspj, csps
- **格式**: JSON文件存储题目信息

### 备份数据 (外部存储)
- **位置**: `/home/metaspeekoj/backups/`
- **说明**: 外部备份文件存储，非项目核心文件
- **内容**: 项目备份文件

## 开发环境配置

### 系统要求
- **操作系统**: Linux
- **Node.js**: v20.19.0
- **Python**: 3.x (在django_env虚拟环境中)
- **包管理器**: npm, pnpm, yarn

### 依赖包目录
- **node_modules**: 前端依赖包目录，由包管理器(npm/pnpm/yarn)自动生成和管理，无需手动维护

### 终端配置
- **Terminal 2**: 前端服务 (webpack-dev-server)
- **Terminal 3**: 后端服务 (Django runserver)
- **Terminal 4-6**: 空闲终端 (可用于其他操作)

## 注意事项

1. 后端服务需要激活 `django_env` 虚拟环境
2. 前端服务使用 webpack-dev-server 提供热重载开发环境
3. 确保两个服务端口不冲突 (前端8080, 后端8086)
4. 项目启动顺序：先启动后端服务，再启动前端服务
5. 选择题功能需要正确的用户权限配置
6. 前端路由配置已修复，避免与后端API路径冲突

## Git仓库信息

- **仓库名称**: metaspeekoj
- **最新提交**: a09a5b7 (2025-09-17 22:51:07)
- **提交信息**: 修复批量导入功能答案格式验证问题，支持A/B/C/D字母答案格式

## 最后更新时间

更新时间: 2025-01-19 (项目文档更新)

