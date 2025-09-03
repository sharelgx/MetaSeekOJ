# 测试文件创建功能使用指南

## 功能概述

新增的 `create_test_file` 功能确保所有创建的测试文件都直接在 `/home/metaspeekoj/TestCode/` 目录下，避免在根目录创建测试文件后再移动的繁琐过程。

## 核心特性

### 🎯 直接创建在TestCode目录
- 所有测试文件直接在 `/home/metaspeekoj/TestCode/` 目录中创建
- 自动确保TestCode目录存在
- 无需手动移动文件

### 📝 智能文件命名
- 自动添加 `test_` 前缀（如果文件名没有以 `test_` 开头或 `_test` 结尾）
- 自动添加文件扩展名（如果没有指定）
- 支持多种文件类型：py, js, html, json, txt等

### 🔄 文件冲突处理
- 如果同名文件已存在，自动创建带时间戳的备份
- 确保不会覆盖现有文件

## 使用方法

### MCP工具调用

```json
{
  "server_name": "test-file-manager",
  "tool_name": "create_test_file",
  "args": {
    "fileName": "example_function",
    "content": "# 测试文件内容\n\ndef test_example():\n    assert True",
    "fileType": "py"
  }
}
```

### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `fileName` | string | ✅ | - | 测试文件名 |
| `content` | string | ❌ | `""` | 文件内容 |
| `fileType` | string | ❌ | `"py"` | 文件扩展名 |

## 使用示例

### 示例1：创建Python测试文件

```json
{
  "fileName": "user_login",
  "content": "import unittest\n\nclass TestUserLogin(unittest.TestCase):\n    def test_valid_login(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()",
  "fileType": "py"
}
```

**结果**：创建 `/home/metaspeekoj/TestCode/test_user_login.py`

### 示例2：创建JavaScript测试文件

```json
{
  "fileName": "api_call",
  "content": "describe('API Call Tests', () => {\n  it('should return valid response', () => {\n    expect(true).toBe(true);\n  });\n});",
  "fileType": "js"
}
```

**结果**：创建 `/home/metaspeekoj/TestCode/test_api_call.js`

### 示例3：创建HTML测试文件

```json
{
  "fileName": "form_validation",
  "content": "<!DOCTYPE html>\n<html>\n<head><title>Form Test</title></head>\n<body>\n  <h1>测试表单验证</h1>\n</body>\n</html>",
  "fileType": "html"
}
```

**结果**：创建 `/home/metaspeekoj/TestCode/test_form_validation.html`

## 文件命名规则

### 自动前缀添加
- 输入：`"user_auth"` → 输出：`"test_user_auth.py"`
- 输入：`"test_login"` → 输出：`"test_login.py"` (保持不变)
- 输入：`"validation_test"` → 输出：`"validation_test.py"` (保持不变)

### 扩展名处理
- 输入：`"api_test"` + `fileType: "js"` → 输出：`"test_api_test.js"`
- 输入：`"test_form.html"` → 输出：`"test_form.html"` (保持不变)

## 响应格式

### 成功响应
```
=== 测试文件创建 ===
✅ 测试文件已创建: test_example.py
文件名: test_example.py
路径: /home/metaspeekoj/TestCode/test_example.py
```

### 错误处理
- 权限不足：显示权限错误信息
- 磁盘空间不足：显示空间不足警告
- 文件名无效：显示命名规范提示

## 与其他功能的配合

### 1. 配合文件检测
```bash
# 先检测根目录的测试文件
detect_test_files

# 移动到TestCode目录
move_test_files

# 创建新的测试文件（直接在TestCode目录）
create_test_file
```

### 2. 配合目录管理
```bash
# 确保TestCode目录存在
ensure_testcode_dir

# 查看TestCode目录状态
get_testcode_status

# 创建新测试文件
create_test_file
```

## 最佳实践

### 📁 目录结构
```
/home/metaspeekoj/
├── TestCode/                    # 所有测试文件的统一位置
│   ├── test_user_auth.py       # 用户认证测试
│   ├── test_api_calls.js       # API调用测试
│   ├── test_form_validation.html # 表单验证测试
│   └── test_data_processing.py  # 数据处理测试
└── [其他项目文件]
```

### 🎯 命名建议
- 使用描述性的文件名：`user_authentication` 而不是 `test1`
- 按功能模块分组：`api_`, `ui_`, `db_` 等前缀
- 保持一致的命名风格

### 🔧 内容模板

**Python测试模板**：
```python
import unittest

class Test{ClassName}(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_{function_name}(self):
        self.assertTrue(True)
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
```

**JavaScript测试模板**：
```javascript
describe('{Module} Tests', () => {
  beforeEach(() => {
    // 设置代码
  });
  
  it('should {expected_behavior}', () => {
    expect(true).toBe(true);
  });
  
  afterEach(() => {
    // 清理代码
  });
});
```

## 技术实现

### 核心逻辑
1. **目录确保**：自动创建TestCode目录（如果不存在）
2. **文件命名**：智能处理文件名和扩展名
3. **冲突处理**：备份现有文件，避免覆盖
4. **错误处理**：完善的异常捕获和用户友好的错误信息

### 安全特性
- 路径验证：确保文件只能在TestCode目录下创建
- 文件名清理：防止路径遍历攻击
- 权限检查：验证写入权限

## 故障排除

### 常见问题

**Q: 文件创建失败**
- 检查TestCode目录权限
- 确认磁盘空间充足
- 验证文件名格式

**Q: 文件被意外备份**
- 同名文件已存在时会自动备份
- 备份文件包含时间戳，可安全删除

**Q: MCP服务器连接失败**
- 确认服务器正在运行
- 检查MCP配置文件
- 重启服务器进程

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2024年
- **兼容性**: Node.js 14+
- **依赖**: fs, path 模块

---

通过这个新功能，您可以确保所有测试文件都在正确的位置创建，提高项目的组织性和可维护性。