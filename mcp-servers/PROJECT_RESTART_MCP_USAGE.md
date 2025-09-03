# MetaSeekOJ 项目重启 MCP 服务使用指南

## 概述

本文档介绍如何使用新集成到 MCP 配置中的项目重启功能。该功能提供了全面的项目重启管理，包含 Redis、前端、后端等所有服务的自动化重启。

## 新增的 MCP 服务器

### 服务器信息
- **服务器名称**: `project-restart`
- **服务器文件**: `/home/metaspeekoj/project_restart_mcp_server.js`
- **工作目录**: `/home/metaspeekoj`
- **依赖**: `@modelcontextprotocol/sdk`

### 配置位置
```json
{
  "mcpServers": {
    "project-restart": {
      "command": "node",
      "args": [
        "/home/metaspeekoj/project_restart_mcp_server.js"
      ],
      "cwd": "/home/metaspeekoj",
      "env": {
        "NODE_PATH": "/home/metaspeekoj/node_modules"
      }
    }
  }
}
```

## 可用工具

### 1. 全面重启项目 (`restart_full_project`)
**功能**: 完整重启所有服务，包括 Redis、Django 后端、Vue.js 前端

**参数**:
- `verbose` (boolean): 是否显示详细输出，默认 true
- `check_status` (boolean): 启动后是否检查服务状态，默认 true

**使用示例**:
```
重启整个项目，包含所有服务
```

### 2. 快速重启 (`quick_restart`)
**功能**: 使用现有的 restart.sh 脚本进行快速重启

**使用示例**:
```
快速重启项目
```

### 3. Python 版本重启 (`python_restart`)
**功能**: 使用 restart_project.py 脚本进行重启

**使用示例**:
```
使用 Python 脚本重启项目
```

### 4. 检查项目状态 (`check_project_status`)
**功能**: 检查所有服务的运行状态

**使用示例**:
```
检查项目状态
```

### 5. 停止所有服务 (`stop_all_services`)
**功能**: 停止前端、后端、Redis 等所有服务

**使用示例**:
```
停止所有项目服务
```

### 6. 仅启动 Redis (`start_redis_only`)
**功能**: 只启动 Redis 服务

**使用示例**:
```
只启动 Redis 服务
```

### 7. 仅启动后端 (`start_backend_only`)
**功能**: 只启动 Django 后端服务

**使用示例**:
```
只启动后端服务
```

### 8. 仅启动前端 (`start_frontend_only`)
**功能**: 只启动 Vue.js 前端服务

**使用示例**:
```
只启动前端服务
```

## 通过 AI 助理使用

### 基本使用方法

1. **全面重启项目**:
   ```
   重启整个项目
   ```
   或
   ```
   全面重启项目，包含所有服务
   ```

2. **快速重启**:
   ```
   快速重启项目
   ```

3. **检查状态**:
   ```
   检查项目运行状态
   ```

4. **停止服务**:
   ```
   停止所有项目服务
   ```

5. **单独启动服务**:
   ```
   只启动 Redis
   ```
   ```
   只启动后端服务
   ```
   ```
   只启动前端服务
   ```

### 高级使用

**带参数的重启**:
```
重启项目，显示详细信息并检查状态
```

**静默重启**:
```
重启项目，不显示详细信息
```

## 工作流程

### 完整重启流程
1. **停止现有服务** - 停止所有运行中的前端、后端、Redis 进程
2. **启动 Redis** - 以守护进程模式启动 Redis 服务器
3. **启动后端** - 启动 Django 开发服务器 (端口 8086)
4. **启动前端** - 启动 Vue.js 开发服务器 (端口 8080)
5. **状态检查** - 验证所有服务是否正常运行
6. **输出结果** - 显示访问地址和日志文件位置

### 服务信息

| 服务 | 端口 | 启动命令 | 日志文件 |
|------|------|----------|----------|
| Redis | 6379 | `redis-server --daemonize yes` | 系统日志 |
| 后端 (Django) | 8086 | `python3 manage.py runserver 0.0.0.0:8086` | `/tmp/backend.log` |
| 前端 (Vue.js) | 8080 | `npm run dev -- --port 8080` | `/tmp/frontend.log` |

### 访问地址
- **前端应用**: http://localhost:8080
- **后端 API**: http://localhost:8086
- **Redis**: localhost:6379

## 技术实现

### MCP 服务器特性
- **异步执行**: 使用 Node.js 异步处理命令执行
- **状态检查**: 实时检查服务端口占用情况
- **错误处理**: 完善的错误捕获和报告机制
- **日志管理**: 自动生成和管理服务日志文件
- **进程管理**: 智能的进程停止和启动管理

### 依赖要求
- Node.js >= 16.0.0
- @modelcontextprotocol/sdk ^0.5.0
- Redis 服务器
- Python 3.x (Django)
- Node.js 和 npm (Vue.js)

## 文件结构

```
/home/metaspeekoj/
├── project_restart_mcp_server.js     # MCP 服务器主文件
├── project_restart_package.json      # 依赖配置文件
├── restart.sh                        # Shell 重启脚本
├── restart_project.py               # Python 重启脚本
├── mcp_project_startup.json         # 原始配置文件
└── PROJECT_RESTART_MCP_USAGE.md     # 本使用说明
```

## 配置备份

在修改 MCP 配置前，系统已自动创建备份：
- **原始配置**: `/home/sharelgx/.trae-server/data/Machine/mcp.json.backup`
- **当前配置**: `/home/sharelgx/.trae-server/data/Machine/mcp.json`

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用: `netstat -tuln | grep -E ':(8080|8086|6379)'`
   - 查看服务日志: `tail -f /tmp/backend.log` 或 `tail -f /tmp/frontend.log`

2. **Redis 连接失败**
   - 检查 Redis 是否运行: `redis-cli ping`
   - 手动启动 Redis: `redis-server --daemonize yes`

3. **MCP 服务器无响应**
   - 检查 Node.js 版本: `node --version`
   - 重新安装依赖: `cd /home/metaspeekoj && npm install`

4. **权限问题**
   - 确保脚本有执行权限: `chmod +x /home/metaspeekoj/project_restart_mcp_server.js`

### 手动重启

如果 MCP 服务不可用，可以使用以下备用方法：

```bash
# 使用 Shell 脚本
bash /home/metaspeekoj/restart.sh

# 使用 Python 脚本
python3 /home/metaspeekoj/restart_project.py
```

## 性能优化

### 启动时间优化
- Redis 启动等待: 2 秒
- 后端启动等待: 5 秒
- 前端启动等待: 5 秒
- 总启动时间: 约 12-15 秒

### 资源使用
- 内存占用: 约 200-500MB (取决于项目大小)
- CPU 使用: 启动期间较高，稳定后较低
- 磁盘 I/O: 主要在日志写入时

## 集成到开发流程

### 推荐工作流程

1. **开发开始**:
   ```
   检查项目状态
   ```
   如果服务未运行:
   ```
   重启整个项目
   ```

2. **代码修改后**:
   ```
   快速重启项目
   ```

3. **调试时**:
   ```
   停止所有服务
   只启动后端服务  # 或只启动前端服务
   ```

4. **开发结束**:
   ```
   停止所有项目服务
   ```

### 与其他工具集成

- **浏览器日志监控**: 可与 `browser-log-monitor` MCP 服务配合使用
- **数据库管理**: 可与 `postgresql` MCP 服务配合使用
- **代码生成**: 可与 `codegen-cli` MCP 服务配合使用

## 扩展开发

### 添加新服务

要添加新的服务到重启流程中，修改 `project_restart_mcp_server.js`：

```javascript
// 在 restartFullProject 方法中添加新服务
async restartFullProject(args = {}) {
  // ... 现有代码 ...
  
  // 添加新服务启动
  output.push('\n6. 启动新服务...');
  const newServiceResult = await this.executeCommand('your-service-start-command');
  if (verbose) {
    output.push(`新服务启动: ${newServiceResult.success ? '成功' : '失败'}`);
  }
  
  // ... 其余代码 ...
}
```

### 自定义配置

可以通过修改以下参数来自定义行为：
- 端口号 (默认 8080, 8086, 6379)
- 等待时间 (默认 2-5 秒)
- 日志文件路径 (默认 `/tmp/`)
- 工作目录路径

## 许可证

MIT License - 详见项目根目录 LICENSE 文件

## 支持

如有问题或建议，请联系 MetaSeekOJ 团队或在项目仓库中提交 Issue。

---

**最后更新**: 2024年1月
**维护者**: MetaSeekOJ Team
**版本**: 1.0.0