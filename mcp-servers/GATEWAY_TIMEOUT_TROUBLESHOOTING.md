# 网关超时问题排查指南

## 问题描述
前端访问API时出现504 Gateway Timeout错误，表现为：
- 前端页面加载时API请求失败
- 浏览器控制台显示504错误
- 前端代理无法正确转发请求到后端

## 问题诊断流程

### 1. 检查后端服务状态
```bash
# 直接测试后端API
curl -I http://localhost:8086/api/website
```
**预期结果**: 返回200状态码表示后端正常

### 2. 检查前端代理状态
```bash
# 测试前端代理
curl -I http://localhost:8080/api/website
```
**问题表现**: 返回504状态码表示代理配置有问题

### 3. 检查前端配置文件
查看 `/home/metaspeekoj/OnlineJudgeFE/config/index.js` 中的代理配置：
```javascript
const commonProxy = {
  target: process.env.TARGET || 'http://localhost:8086', // 确保端口正确
  changeOrigin: true
}
```

## 常见问题和解决方案

### 问题1: 代理端口配置错误
**症状**: 前端代理指向错误的后端端口
**解决**: 修改 `config/index.js` 中的目标端口从8000改为8086

### 问题2: 服务重启后配置未生效
**症状**: 修改配置后仍然出现504错误
**解决**: 完全停止并重启所有服务
```bash
# 使用MCP服务重启
# 1. 停止所有服务
# 2. 重新启动项目
```

### 问题3: 前端服务启动不完整
**症状**: 前端进程存在但代理功能异常
**解决**: 检查前端启动日志，确保代理配置正确加载

## 完整解决步骤

1. **诊断问题**
   - 测试后端API直接访问
   - 测试前端代理访问
   - 确认问题出现在代理层

2. **修复配置**
   - 检查并修正前端代理配置
   - 确保目标端口正确(8086)

3. **重启服务**
   - 停止所有服务
   - 重新启动完整项目
   - 等待服务完全初始化

4. **验证修复**
   - 测试API代理访问
   - 确认返回200状态码
   - 验证前端页面正常加载

## 预防措施

1. **配置管理**
   - 使用环境变量管理端口配置
   - 定期检查配置文件一致性

2. **监控检查**
   - 定期测试API连通性
   - 监控服务启动状态

3. **文档维护**
   - 记录端口分配规则
   - 更新部署文档

## 相关文件
- `/home/metaspeekoj/OnlineJudgeFE/config/index.js` - 前端代理配置
- `/tmp/frontend.log` - 前端服务日志
- `/tmp/backend.log` - 后端服务日志

## MCP集成使用

### 自动故障排除
现在可以通过MCP服务器直接使用自动化故障排除功能：

```
# 通过AI助理使用
"请诊断504网关超时问题"
"请自动修复网关超时问题"
```

### MCP工具功能
- **troubleshoot_gateway_timeout**: 自动诊断和修复504错误
  - `auto_fix`: 是否自动尝试修复问题 (默认: true)
  - `check_config`: 是否检查前端代理配置 (默认: true)

### 自动化流程
1. **自动诊断**
   - 检查后端服务状态 (端口8086)
   - 检查前端代理状态 (端口8080)
   - 验证前端配置文件
   - 检查服务进程状态

2. **自动修复**
   - 自动修正代理配置错误
   - 重启相关服务
   - 验证修复结果

3. **智能报告**
   - 详细的诊断结果
   - 具体的修复建议
   - 参考文档链接

## 快速检查命令
```bash
# 检查所有服务状态
ps aux | grep -E '(node.*dev-server|python.*manage.py|redis)'

# 测试API连通性
curl -I http://localhost:8080/api/website
curl -I http://localhost:8086/api/website

# 查看服务日志
tail -f /tmp/frontend.log
tail -f /tmp/backend.log
```

## MCP服务器信息
- **服务器文件**: `/home/metaspeekoj/mcp-servers/project_restart_mcp_server.js`
- **配置位置**: MCP配置中的 `project-restart` 服务器
- **依赖**: @modelcontextprotocol/sdk

---
*最后更新: 2025-09-02*
*MCP集成: 已添加自动化故障排除功能*
*问题解决记录: 504网关超时问题通过修正前端代理配置和完整重启服务得到解决*