# WSL MCP 环境启动说明

## 概述
本文档说明如何使用Windows批处理文件来启动WSL环境并确保MCP服务器正常运行。

## 文件说明

### 1. start_wsl_mcp.bat (完整版)
- **功能**: 完整的WSL MCP环境检查和启动
- **特点**: 
  - 检查WSL状态
  - 验证MCP服务器文件
  - 测试所有MCP服务器启动
  - 验证配置文件
  - 显示详细状态信息

### 2. quick_start_mcp.bat (快速版)
- **功能**: 快速启动WSL MCP环境
- **特点**:
  - 简化的启动流程
  - 基本环境检查
  - 适合日常使用

## 使用方法

### Windows端操作
1. 将批处理文件复制到Windows系统中（如 `C:\Users\Public\`）
2. 双击运行批处理文件
3. 等待WSL环境启动完成
4. 启动Trae IDE

### 推荐使用流程
1. **首次使用**: 运行 `start_wsl_mcp.bat` 进行完整检查
2. **日常使用**: 运行 `quick_start_mcp.bat` 快速启动

## MCP服务器列表

当前配置的MCP服务器：
- **test-file-manager**: 测试文件管理工具
- **browser-log-monitor**: 浏览器日志监控工具
- **project-restart**: 项目重启工具
- **playwright**: 浏览器自动化工具
- **postgresql**: PostgreSQL数据库工具
- **GitHub**: GitHub代码仓库工具

## 故障排除

### 常见问题
1. **WSL未启动**: 确保WSL已安装并启用
2. **权限问题**: 确保以管理员身份运行批处理文件
3. **MCP服务器启动失败**: 检查Node.js环境和依赖包

### 检查命令
```bash
# 在WSL中检查MCP服务器状态
cd /home/metaspeekoj/mcp-servers
node project_restart_mcp_server.js --version
node browser_log_mcp_server.js --version
node test_file_manager_mcp_server.js --version
```

## 配置文件位置
- **MCP配置**: `/home/sharelgx/.trae-server/data/Machine/mcp.json`
- **服务器文件**: `/home/metaspeekoj/mcp-servers/`
- **依赖包**: `/home/metaspeekoj/mcp-servers/node_modules/`

## 注意事项
1. 确保WSL Ubuntu发行版已正确安装
2. 确保用户 `metaspeekoj` 存在且有适当权限
3. 确保sudo密码为 `123456`（如有变更请修改脚本）
4. 建议在启动Trae IDE前运行批处理文件

---
*创建时间: 2025-01-13*
*适用于: WSL Ubuntu + Trae IDE + MCP环境*