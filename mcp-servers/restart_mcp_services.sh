#!/bin/bash

# 重启MCP服务脚本
echo "正在重启MCP服务..."

# 检查MCP配置文件
echo "检查MCP配置文件:"
if [ -f "/home/sharelgx/.trae-server/data/Machine/mcp.json" ]; then
    echo "✓ MCP配置文件存在"
    echo "test-file-manager配置:"
    grep -A 10 "test-file-manager" /home/sharelgx/.trae-server/data/Machine/mcp.json
else
    echo "✗ MCP配置文件不存在"
fi

# 检查服务器进程
echo "\n检查MCP服务器进程:"
ps aux | grep "test_file_manager_mcp_server.js" | grep -v grep

# 提示用户重启IDE
echo "\n=== 解决方案 ==="
echo "1. test-file-manager服务器正在运行"
echo "2. MCP配置文件已正确配置"
echo "3. 请重启Trae AI IDE或重新加载MCP配置"
echo "4. 重启后，test-file-manager工具应该可以使用"

echo "\n可用的test-file-manager工具:"
echo "- create_test_file: 创建测试文件"
echo "- move_test_files: 移动测试文件到TestCode目录"
echo "- list_test_files: 列出测试文件"
echo "- clean_test_files: 清理测试文件"
echo "- get_test_directory: 获取测试目录信息"
echo "- validate_test_structure: 验证测试结构"

echo "\n脚本执行完成。请重启Trae AI IDE。"