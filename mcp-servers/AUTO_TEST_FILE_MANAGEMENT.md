# 自动测试文件管理系统

## 概述

测试文件管理功能已成功集成到MCP配置中，可以自动检测和管理项目中的测试文件。当系统需要测试时，可以直接在 `/home/metaspeekoj/TestCode/` 文件夹下创建相关文件，或者让系统自动将根目录下的测试文件移动到该目录。

## 自动化功能特性

### 🔍 智能检测
- 自动识别根目录下的测试文件
- 支持多种测试文件命名模式：
  - `test_*.py/js/html/json/txt`
  - `*_test.py/js/html/json/txt`
  - `debug_*.py/js/html/json/txt`
  - `check_*.py/js/html/json/txt`
  - `assign_*.py/js/html/json/txt`
  - `*.test.py/js/html/json/txt`

### 🚀 自动管理
- 自动将测试文件移动到 `TestCode` 目录
- 保持文件完整性和权限
- 避免重复移动
- 自动创建目标目录

### 📊 状态监控
- 实时检测测试文件状态
- 提供详细的移动报告
- 显示文件大小和修改时间

## MCP配置状态

✅ **已配置完成**

测试文件管理服务器已成功添加到MCP配置文件：
```json
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
```

## 可用指令

### 1. 检测测试文件
```bash
# 通过MCP协议调用
detect_test_files
```

### 2. 移动测试文件
```bash
# 移动所有检测到的测试文件
move_test_files

# 移动指定文件
move_test_files --files ["test1.py", "test2.js"]
```

### 3. 查看TestCode目录状态
```bash
get_testcode_status
```

### 4. 清理根目录测试文件
```bash
clean_root_test_files
```

### 5. 确保TestCode目录存在
```bash
ensure_testcode_dir
```

## 使用示例

### 场景1：创建新测试文件
当需要测试时，直接在 `/home/metaspeekoj/TestCode/` 目录下创建测试文件：

```bash
# 在TestCode目录下创建测试文件
echo 'print("Hello Test")' > /home/metaspeekoj/TestCode/test_new_feature.py
```

### 场景2：自动管理现有测试文件
如果在根目录创建了测试文件，系统会自动检测并提供移动选项：

```bash
# 在根目录创建测试文件
echo 'console.log("Test");' > /home/metaspeekoj/test_example.js

# 系统会自动检测到该文件，并可通过MCP指令移动
```

## 验证测试

✅ **功能验证完成**

1. **检测功能**：成功检测到 `test_auto_detection.py`
2. **移动功能**：成功将文件从根目录移动到 `TestCode` 目录
3. **清理功能**：根目录下的测试文件已被清理
4. **MCP集成**：服务器正常响应MCP协议请求

## 目录结构

```
/home/metaspeekoj/
├── TestCode/                    # 测试文件统一存放目录
│   ├── assign_questions.py
│   ├── check_questions.py
│   ├── debug_questions.py
│   ├── test_api.py
│   ├── test_auto_detection.py   # 新移动的测试文件
│   ├── test_image_resize.html
│   └── test_login_status.html
└── mcp-servers/                 # MCP服务器文件
    ├── test_file_manager_mcp_server.js
    ├── test_file_manager_package.json
    └── AUTO_TEST_FILE_MANAGEMENT.md
```

## 技术实现

- **协议**：MCP (Model Context Protocol) 2024-11-05
- **运行时**：Node.js
- **文件系统**：原生 fs 模块
- **进程管理**：child_process 模块
- **配置文件**：`/home/sharelgx/.trae-server/data/Machine/mcp.json`

## 安全特性

- 只处理指定目录下的文件
- 验证文件路径安全性
- 保持文件权限不变
- 提供详细的操作日志

## 故障排除

### 服务器未响应
```bash
# 检查服务器进程
ps aux | grep test_file_manager

# 重启服务器
pkill -f test_file_manager_mcp_server.js
cd /home/metaspeekoj/mcp-servers
node test_file_manager_mcp_server.js
```

### MCP工具未找到
```bash
# 验证MCP配置
grep -A 10 'test-file-manager' /home/sharelgx/.trae-server/data/Machine/mcp.json
```

## 最佳实践

1. **统一管理**：所有测试文件都放在 `TestCode` 目录下
2. **命名规范**：使用标准的测试文件命名模式
3. **定期清理**：定期运行清理指令，保持根目录整洁
4. **状态监控**：定期检查 `TestCode` 目录状态

---

**状态**：✅ 已部署并验证  
**最后更新**：2025年9月2日  
**版本**：1.0.0