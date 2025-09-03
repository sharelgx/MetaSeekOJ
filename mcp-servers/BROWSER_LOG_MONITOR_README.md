# 浏览器日志自动监控工具

这个工具可以监控代码文件的变化，并自动获取浏览器控制台日志，帮助开发者快速发现和调试问题。

## 功能特性

- 🔍 **文件监控**: 自动监控指定目录下的代码文件变化
- 🌐 **浏览器自动化**: 使用Playwright自动打开浏览器并获取日志
- 📝 **日志收集**: 收集控制台日志、网络错误、页面错误
- 🔧 **MCP集成**: 利用现有的MCP playwright服务器
- ⚡ **智能防抖**: 避免频繁触发，提高效率
- 📊 **日志分析**: 自动分析常见问题并提供建议

## 文件说明

### 核心文件

1. **`auto_browser_log_monitor.py`** - 基础版本，直接使用Playwright
2. **`mcp_browser_log_monitor.py`** - MCP集成版本，利用现有MCP配置
3. **`browser_log_config.json`** - 配置文件
4. **`setup_browser_monitor.sh`** - 安装脚本

### 生成的日志文件

- **`browser_logs_YYYYMMDD_HHMMSS.json`** - 完整的浏览器日志数据
- **`browser_summary_YYYYMMDD_HHMMSS.txt`** - 可读的日志摘要
- **`browser_log_monitor.log`** - 监控工具运行日志
- **`mcp_browser_monitor.log`** - MCP版本运行日志

## 安装步骤

### 1. 运行安装脚本

```bash
chmod +x setup_browser_monitor.sh
./setup_browser_monitor.sh
```

### 2. 手动安装（如果脚本失败）

```bash
# 安装Python依赖
pip3 install watchdog playwright requests

# 安装Playwright浏览器
python3 -m playwright install chromium

# 验证Node.js和npm
node --version
npm --version
```

## 配置说明

编辑 `browser_log_config.json` 文件来自定义监控行为：

```json
{
  "watch_directories": [
    "./OnlineJudgeFE/src",  // 监控的目录
    "./OnlineJudge"
  ],
  "watch_extensions": [
    ".vue", ".js", ".py", ".html", ".css"  // 监控的文件类型
  ],
  "target_url": "http://localhost:8080",  // 目标网站URL
  "headless": false,  // 是否无头模式（false可以看到浏览器）
  "wait_time": 5000,  // 页面加载等待时间（毫秒）
  "custom_js": "console.log('测试开始');",  // 自定义JavaScript代码
  "specific_pages": {  // 特定页面URL
    "practice_mode": "http://localhost:8080/choice-question-practice?category=3",
    "exam_mode": "http://localhost:8080/choice-questions?category=3"
  },
  "auto_actions": {  // 自动化操作
    "click_practice_button": true,  // 自动点击练习按钮
    "wait_for_questions": true,     // 等待题目加载
    "capture_network_errors": true  // 捕获网络错误
  }
}
```

## 使用方法

### 基础版本

```bash
# 启动基础监控
python3 auto_browser_log_monitor.py
```

### MCP集成版本（推荐）

```bash
# 启动MCP集成监控
python3 mcp_browser_log_monitor.py
```

### 使用流程

1. **启动监控工具**
   ```bash
   python3 mcp_browser_log_monitor.py
   ```

2. **确保前端服务器运行**
   ```bash
   cd OnlineJudgeFE
   npm run dev
   ```

3. **修改代码文件**
   - 编辑任何被监控的文件（.vue, .js, .py等）
   - 保存文件

4. **自动获取日志**
   - 工具会自动检测文件变化
   - 启动浏览器访问目标页面
   - 收集控制台日志和网络错误
   - 保存日志到文件

## 日志分析

### 控制台日志类型

- **log**: 普通日志信息
- **warn**: 警告信息
- **error**: 错误信息
- **info**: 信息日志
- **debug**: 调试信息

### 常见问题检测

工具会自动检测以下问题：

- ✅ **未定义属性访问**: `Cannot read properties of undefined`
- ✅ **网络请求失败**: `Failed to fetch`
- ✅ **Vue警告**: `Vue warn`
- ✅ **网络错误**: HTTP请求失败
- ✅ **页面错误**: JavaScript运行时错误

### 日志文件示例

**browser_summary_20240121_143022.txt**
```
文件变化: /home/user/OnlineJudgeFE/src/pages/PracticeMode.vue
测试时间: 2024-01-21T14:30:22.123Z
页面URL: http://localhost:8080/choice-question-practice?category=3

=== 控制台日志 ===
[LOG] 自动化测试开始 - 2024/1/21 下午2:30:22
[ERROR] Cannot read properties of undefined (reading 'length')
[WARN] Vue component received non-prop attributes

=== 网络错误 ===
[GET] http://localhost:8000/api/choice-questions - net::ERR_CONNECTION_REFUSED
```

## 高级功能

### 自定义JavaScript注入

在配置文件中设置 `custom_js` 来注入自定义代码：

```json
{
  "custom_js": "window.testMode = true; console.log('测试模式已启用'); localStorage.setItem('debug', 'true');"
}
```

### 特定页面测试

配置不同的页面URL进行针对性测试：

```json
{
  "specific_pages": {
    "practice_mode": "http://localhost:8080/choice-question-practice?category=3",
    "exam_mode": "http://localhost:8080/choice-questions?category=3",
    "wrong_questions": "http://localhost:8080/wrong-questions"
  }
}
```

### 自动化操作

配置自动化操作来模拟用户行为：

```json
{
  "auto_actions": {
    "click_practice_button": true,
    "wait_for_questions": true,
    "fill_form_data": true
  }
}
```

## 故障排除

### 常见问题

1. **"Node.js 未安装"**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # 或使用nvm
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 18
   ```

2. **"Playwright 浏览器未安装"**
   ```bash
   python3 -m playwright install chromium
   ```

3. **"权限被拒绝"**
   ```bash
   chmod +x *.py
   chmod +x *.sh
   ```

4. **"监控目录不存在"**
   - 检查配置文件中的路径是否正确
   - 确保相对路径从正确的工作目录开始

### 调试模式

设置环境变量启用详细日志：

```bash
export PYTHONPATH=.
export DEBUG=1
python3 mcp_browser_log_monitor.py
```

### 测试配置

创建测试配置文件 `test_config.json`：

```json
{
  "watch_directories": ["./test"],
  "watch_extensions": [".txt"],
  "target_url": "http://localhost:8080",
  "headless": false,
  "wait_time": 2000
}
```

## 性能优化

### 减少资源消耗

1. **启用无头模式**
   ```json
   { "headless": true }
   ```

2. **调整防抖时间**
   ```python
   self.debounce_time = 5  # 增加到5秒
   ```

3. **限制监控范围**
   ```json
   {
     "watch_directories": ["./src/components"],  // 只监控特定目录
     "watch_extensions": [".vue"]              // 只监控特定文件类型
   }
   ```

## 集成到开发流程

### 与Git Hooks集成

创建 `.git/hooks/post-commit`：

```bash
#!/bin/bash
echo "代码提交后自动测试..."
python3 /path/to/mcp_browser_log_monitor.py --single-run
```

### 与CI/CD集成

在 `.github/workflows/test.yml` 中添加：

```yaml
- name: Browser Log Test
  run: |
    python3 mcp_browser_log_monitor.py --headless --single-run
    cat browser_summary_*.txt
```

## 扩展开发

### 添加新的日志分析规则

在 `analyze_logs` 方法中添加：

```python
def analyze_logs(self, log_data):
    # 现有代码...
    
    # 添加自定义规则
    for log in console_logs:
        text = log['text'].lower()
        if 'custom_error_pattern' in text:
            issues.append("发现自定义错误模式")
```

### 添加新的自动化操作

在 `generate_auto_actions` 方法中添加：

```python
if auto_config.get('custom_action'):
    actions.append('''
    // 自定义操作
    try {
        await page.click('#custom-button');
        console.log('执行了自定义操作');
    } catch (e) {
        console.log('自定义操作失败');
    }''')
```

## 许可证

本工具基于MIT许可证开源，可自由使用和修改。

## 支持

如有问题或建议，请查看日志文件或联系开发团队。