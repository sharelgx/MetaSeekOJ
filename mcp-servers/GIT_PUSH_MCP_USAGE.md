# Git推送MCP服务器使用指南

## 概述

Git推送MCP服务器是一个专门用于处理Git版本控制操作的MCP（Model Context Protocol）服务器。它提供了完整的Git推送工作流，包括文件添加、提交、标签管理和推送到远程仓库等功能。

## 功能特性

### 🚀 核心功能
- **一键推送**: `git_push_all` - 自动执行添加、提交、推送的完整流程
- **状态检查**: `git_status` - 查看当前Git仓库状态
- **分步操作**: `git_add_commit` - 单独执行添加和提交操作
- **推送管理**: `git_push` - 灵活的推送配置

### 🏷️ 标签支持
- 自动创建和推送标签
- 支持带注释的标签
- 批量标签推送

### 🔧 智能特性
- 自动检测文件变更
- 智能错误处理和报告
- 支持自定义提交信息
- 灵活的远程仓库配置

## 安装配置

### 1. 文件结构
```
/home/metaspeekoj/mcp-servers/
├── git_push_mcp_server.js      # MCP服务器主文件
├── git_push_package.json       # 依赖配置文件
└── GIT_PUSH_MCP_USAGE.md       # 本使用说明
```

### 2. 依赖安装
```bash
cd /home/metaspeekoj/mcp-servers
npm install --package-lock-only
```

### 3. MCP配置
在Trae AI的MCP配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "git-push": {
      "command": "node",
      "args": ["/home/metaspeekoj/mcp-servers/git_push_mcp_server.js"],
      "cwd": "/home/metaspeekoj/mcp-servers"
    }
  }
}
```

## 工具详解

### 1. git_push_all - 一键推送

**功能**: 执行完整的Git推送流程

**参数**:
- `commit_message` (可选): 提交信息，默认为"自动提交：更新项目文件"
- `add_tag` (可选): 是否添加标签，默认为false
- `tag_name` (可选): 标签名称
- `tag_message` (可选): 标签信息

**执行流程**:
1. 检查Git状态
2. 添加所有修改的文件 (`git add .`)
3. 提交更改 (`git commit`)
4. 创建标签（如果指定）
5. 推送到远程仓库 (`git push origin main`)
6. 推送标签（如果有）
7. 显示最终状态

**使用示例**:
```javascript
// 基本推送
{
  "commit_message": "修复考试分数计算问题"
}

// 带标签推送
{
  "commit_message": "发布版本v1.2.0",
  "add_tag": true,
  "tag_name": "v1.2.0",
  "tag_message": "修复考试分数计算问题，优化前端界面"
}
```

### 2. git_status - 状态检查

**功能**: 查看当前Git仓库状态和修改的文件

**参数**: 无

**返回信息**:
- 当前分支状态
- 暂存区文件
- 工作区修改
- 未跟踪文件

### 3. git_add_commit - 添加和提交

**功能**: 将文件添加到暂存区并提交

**参数**:
- `files` (可选): 要添加的文件列表，默认为["."]（所有文件）
- `commit_message` (可选): 提交信息

**使用示例**:
```javascript
// 提交所有文件
{
  "commit_message": "更新前端组件"
}

// 提交指定文件
{
  "files": ["src/components/", "package.json"],
  "commit_message": "更新组件和依赖"
}
```

### 4. git_push - 推送操作

**功能**: 推送代码到远程仓库

**参数**:
- `remote` (可选): 远程仓库名称，默认为"origin"
- `branch` (可选): 分支名称，默认为"main"
- `push_tags` (可选): 是否推送标签，默认为false

**使用示例**:
```javascript
// 基本推送
{
  "remote": "origin",
  "branch": "main"
}

// 推送并包含标签
{
  "remote": "origin",
  "branch": "main",
  "push_tags": true
}
```

## 使用场景

### 场景1: 日常开发推送
```javascript
// 使用git_push_all进行快速推送
{
  "commit_message": "实现用户登录功能"
}
```

### 场景2: 版本发布
```javascript
// 创建版本标签并推送
{
  "commit_message": "发布版本v2.1.0",
  "add_tag": true,
  "tag_name": "v2.1.0",
  "tag_message": "新增选择题功能，修复已知问题"
}
```

### 场景3: 分步操作
```javascript
// 1. 先检查状态
git_status

// 2. 添加和提交
{
  "files": ["frontend/", "backend/models/"],
  "commit_message": "更新前后端模型"
}

// 3. 推送
{
  "remote": "origin",
  "branch": "main"
}
```

## 错误处理

### 常见错误及解决方案

1. **推送失败 - 认证问题**
   - 检查GitHub访问令牌
   - 确认仓库权限

2. **提交失败 - 没有更改**
   - 服务器会自动检测并提示
   - 不会中断操作流程

3. **标签冲突**
   - 检查标签是否已存在
   - 使用不同的标签名称

4. **网络问题**
   - 检查网络连接
   - 重试推送操作

## 最佳实践

### 1. 提交信息规范
```javascript
// 好的提交信息
"修复: 考试分数计算错误"
"新增: 用户权限管理功能"
"优化: 前端页面加载性能"
"文档: 更新API使用说明"

// 避免的提交信息
"修改"
"更新"
"fix"
```

### 2. 标签命名规范
```javascript
// 语义化版本
"v1.0.0"    // 主版本
"v1.1.0"    // 次版本
"v1.1.1"    // 补丁版本

// 功能标签
"feature-user-auth"     // 功能分支
"hotfix-score-calc"     // 热修复
"release-2025.01"       // 发布版本
```

### 3. 工作流建议
```javascript
// 开发阶段 - 频繁小提交
git_add_commit({
  "commit_message": "实现登录表单验证"
})

// 功能完成 - 推送到远程
git_push({
  "remote": "origin",
  "branch": "feature-login"
})

// 版本发布 - 一键推送带标签
git_push_all({
  "commit_message": "发布用户认证功能",
  "add_tag": true,
  "tag_name": "v1.2.0",
  "tag_message": "新增用户认证和权限管理"
})
```

## 故障排除

### 检查服务器状态
```bash
# 检查MCP服务器进程
ps aux | grep git_push_mcp_server.js

# 手动启动服务器
cd /home/metaspeekoj/mcp-servers
node git_push_mcp_server.js
```

### 验证Git配置
```bash
# 检查Git配置
git config --list

# 检查远程仓库
git remote -v

# 测试连接
git ls-remote origin
```

### 日志调试
服务器会输出详细的操作日志，包括：
- 命令执行状态
- 错误信息和堆栈
- 操作结果反馈

## 扩展功能

未来可以扩展的功能：
- 分支管理操作
- 合并请求创建
- 冲突解决辅助
- 批量仓库操作
- Git钩子集成

## 技术实现

### 核心技术
- **Node.js**: 服务器运行环境
- **@modelcontextprotocol/sdk**: MCP协议实现
- **child_process**: Git命令执行
- **Promise/async**: 异步操作处理

### 安全考虑
- 命令注入防护
- 路径遍历保护
- 错误信息过滤
- 权限检查机制

---

**版本**: 1.0.0  
**最后更新**: 2025年1月14日  
**维护者**: MetaSeekOJ项目团队  
**许可证**: MIT License