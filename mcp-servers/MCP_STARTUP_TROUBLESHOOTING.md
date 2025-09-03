# MCP 测试文件管理服务器启动故障排除

## 当前状态分析

✅ **服务器运行状态**: 正常运行  
✅ **协议版本**: 2024-11-05  
✅ **服务器信息**: test-file-manager v1.0.0  
✅ **工具列表**: 已发送更新通知  

## 问题诊断

根据当前情况，测试文件管理MCP服务器实际上**正在正常运行**，但可能存在以下问题：

### 1. MCP配置问题 ⚠️

**问题**: MCP配置文件缺少 `cwd` 参数，导致IDE无法正确连接到服务器。

**当前可能的配置**:
```json
{
  "mcpServers": {
    "test-file-manager": {
      "command": "node",
      "args": [
        "/home/metaspeekoj/mcp-servers/test_file_manager_mcp_server.js"
      ],
      "env": {
        "NODE_PATH": "/home/metaspeekoj/node_modules"
      }
    }
  }
}
```

**需要的正确配置**:
```json
{
  "mcpServers": {
    "test-file-manager": {
      "command": "node",
      "args": [
        "/home/metaspeekoj/mcp-servers/test_file_manager_mcp_server.js"
      ],
      "cwd": "/home/metaspeekoj/mcp-servers",
      "env": {
        "NODE_PATH": "/home/metaspeekoj/node_modules"
      }
    }
  }
}
```

### 2. 连接超时问题 ⏱️

服务器可能需要更长时间来完全初始化所有工具。

## 解决方案

### 方案1: 修复MCP配置 (推荐)

1. **打开MCP配置文件**
   ```bash
   # 配置文件位置
   /home/sharelgx/.trae-server/data/Machine/mcp.json
   ```

2. **添加cwd参数**
   在 `test-file-manager` 配置中添加:
   ```json
   "cwd": "/home/metaspeekoj/mcp-servers"
   ```

3. **重启IDE或重新加载MCP配置**

### 方案2: 验证服务器功能

可以通过以下方式测试服务器是否正常工作:

```bash
# 检查服务器进程
ps aux | grep test_file_manager

# 查看服务器日志
tail -f /home/metaspeekoj/mcp-servers/server.log
```

### 方案3: 手动重启服务器

```bash
# 停止当前服务器
pkill -f test_file_manager_mcp_server.js

# 重新启动
cd /home/metaspeekoj/mcp-servers
node test_file_manager_mcp_server.js
```

## 可用功能验证

一旦连接成功，以下功能应该可用:

### 🔧 核心工具
1. `detect_test_files` - 检测根目录测试文件
2. `move_test_files` - 移动测试文件到TestCode目录
3. `get_testcode_status` - 查看TestCode目录状态
4. `clean_root_test_files` - 清理根目录测试文件
5. `ensure_testcode_dir` - 确保TestCode目录存在
6. `create_test_file` - 直接在TestCode目录创建测试文件

### 📁 目录结构
```
/home/metaspeekoj/
├── TestCode/                    # 测试文件统一存放目录
│   ├── test_*.py               # Python测试文件
│   ├── test_*.js               # JavaScript测试文件
│   ├── test_*.html             # HTML测试文件
│   └── ...
└── mcp-servers/                # MCP服务器文件
    ├── test_file_manager_mcp_server.js
    └── ...
```

## 状态监控

### 检查服务器状态
```bash
# 检查进程
ps aux | grep "test_file_manager_mcp_server.js"

# 检查端口（如果适用）
netstat -tuln | grep :PORT

# 检查日志
tail -f /tmp/mcp-server.log
```

### 验证MCP连接
服务器启动后应该看到以下输出:
```json
{"jsonrpc":"2.0","result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"serverInfo":{"name":"test-file-manager","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/tools/list_changed","params":{}}
```

## 常见错误及解决

### 错误1: "服务器准备中"
- **原因**: MCP配置缺少cwd参数
- **解决**: 添加 `"cwd": "/home/metaspeekoj/mcp-servers"`

### 错误2: "连接超时"
- **原因**: 服务器启动时间过长
- **解决**: 等待更长时间或重启服务器

### 错误3: "工具未找到"
- **原因**: 服务器未完全初始化
- **解决**: 检查服务器日志，确认所有工具已加载

## 联系支持

如果问题仍然存在，请提供:
1. MCP配置文件内容
2. 服务器启动日志
3. IDE错误信息
4. 系统环境信息

---

**最后更新**: 2025年1月2日  
**状态**: 服务器运行正常，需要修复MCP配置  
**版本**: 1.0.0