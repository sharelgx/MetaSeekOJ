# MCP 浏览器日志监控使用指南

## 概述

我已经成功将浏览器日志监控功能集成到 MCP (Model Context Protocol) 配置中。现在你可以通过 MCP 工具直接使用自动化浏览器日志监控功能。

## 配置详情

### 新增的 MCP 服务器
- **服务器名称**: `browser-log-monitor`
- **配置文件**: `/home/sharelgx/.trae-server/data/Machine/mcp.json`
- **服务器脚本**: `/home/metaspeekoj/browser_log_mcp_server.js`

### 可用工具

1. **start_browser_log_monitor**
   - 功能：启动文件监控和自动浏览器日志捕获
   - 参数：
     - `watchDirectory`: 监控的目录（默认：`/home/metaspeekoj/OnlineJudgeFE/src`）
     - `targetUrl`: 目标URL（默认：`http://localhost:8080`）
     - `fileExtensions`: 监控的文件扩展名（默认：`.vue`, `.js`, `.ts`, `.css`）

2. **stop_browser_log_monitor**
   - 功能：停止浏览器日志监控
   - 参数：无

3. **get_latest_browser_logs**
   - 功能：获取最新的浏览器日志
   - 参数：
     - `logFile`: 日志文件路径（默认：`/home/metaspeekoj/browser_logs.txt`）

## 使用方法

### 通过 AI 助理使用

现在你可以直接对我说：

1. **启动监控**：
   ```
   "请启动浏览器日志监控，监控 OnlineJudgeFE/src 目录"
   ```

2. **停止监控**：
   ```
   "请停止浏览器日志监控"
   ```

3. **查看日志**：
   ```
   "请显示最新的浏览器日志"
   ```

### 工作流程

1. **自动触发**：当你修改 `.vue`, `.js`, `.ts`, `.css` 文件时
2. **自动执行**：系统会自动启动 Playwright 浏览器
3. **自动捕获**：访问指定URL并捕获控制台日志和错误
4. **自动保存**：日志会自动保存到 `/home/metaspeekoj/browser_logs.txt`

## 技术实现

### MCP 集成优势
- **无需手动启动脚本**：通过 MCP 协议自动管理
- **与 AI 助理深度集成**：可以通过自然语言控制
- **实时状态管理**：AI 助理可以实时了解监控状态
- **智能日志分析**：AI 助理可以分析和解释日志内容

### 文件结构
```
/home/metaspeekoj/
├── browser_log_mcp_server.js     # MCP 服务器脚本
├── browser_log_mcp_package.json  # 依赖配置
├── node_modules/                 # Node.js 依赖
├── browser_logs.txt              # 自动生成的日志文件
└── MCP_BROWSER_LOG_USAGE.md      # 本使用说明

/home/sharelgx/.trae-server/data/Machine/
└── mcp.json                      # 更新后的 MCP 配置
```

## 配置备份

原始 MCP 配置已备份到：
`/home/sharelgx/.trae-server/data/Machine/mcp.json.backup`

## 故障排除

### 如果监控不工作
1. 检查 Node.js 依赖是否安装：
   ```bash
   cd /home/metaspeekoj && npm list
   ```

2. 检查 MCP 服务器状态：
   ```bash
   node /home/metaspeekoj/browser_log_mcp_server.js
   ```

3. 检查日志文件权限：
   ```bash
   ls -la /home/metaspeekoj/browser_logs.txt
   ```

### 恢复原始配置
如需恢复原始 MCP 配置：
```bash
cp /home/sharelgx/.trae-server/data/Machine/mcp.json.backup /home/sharelgx/.trae-server/data/Machine/mcp.json
```

## 高级功能

### 自定义监控配置
你可以通过 AI 助理自定义监控参数：
- 监控不同的目录
- 监控不同的文件类型
- 监控不同的URL
- 调整日志捕获策略

### 日志分析
AI 助理现在可以：
- 自动分析浏览器错误
- 识别常见问题模式
- 提供修复建议
- 跟踪性能指标

## 总结

通过 MCP 集成，浏览器日志监控现在完全自动化，你只需要：
1. 正常编辑代码文件
2. 系统自动捕获浏览器日志
3. 通过 AI 助理查看和分析日志

这实现了真正的"每次修改文件后自动获取浏览器日志"的功能！