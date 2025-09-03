# MCP Test File Manager 准备中问题修复指南

## 问题描述
MCP配置中的test-file-manager服务器一直显示"准备中"状态，无法正常使用。

## 问题原因
MCP配置缺少工作目录(cwd)设置，导致服务器无法正确初始化。

## 解决方案

### 当前配置
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

### 修复后的配置
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

## 修复步骤

1. **打开MCP配置文件**
   - 文件路径: `/home/sharelgx/.trae-server/data/Machine/mcp.json`

2. **添加cwd参数**
   - 在test-file-manager配置中添加: `"cwd": "/home/metaspeekoj/mcp-servers"`

3. **重启MCP服务**
   - 保存配置文件后，MCP会自动重新加载配置

## 验证修复

修复后，test-file-manager应该能够正常工作，提供以下功能：

- `detect_test_files` - 检测测试文件
- `move_test_files` - 移动测试文件
- `get_testcode_status` - 获取TestCode目录状态
- `clean_root_test_files` - 清理根目录测试文件
- `ensure_testcode_dir` - 确保TestCode目录存在

## 其他可能的问题

如果添加cwd后仍然有问题，请检查：

1. **文件权限**: 确保MCP有权限访问服务器文件
2. **Node.js路径**: 确保NODE_PATH正确设置
3. **服务器文件**: 确保test_file_manager_mcp_server.js文件存在且可执行

## 联系支持

如果问题仍然存在，请提供：
- MCP日志信息
- 服务器启动日志
- 系统环境信息