#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP配置修复脚本
用于修复test-file-manager服务器的MCP配置问题
"""

import json
import os
import shutil
from datetime import datetime

def fix_mcp_config():
    """
    修复MCP配置文件，添加缺失的cwd参数
    """
    
    # MCP配置文件路径
    config_path = '/home/sharelgx/.trae-server/data/Machine/mcp.json'
    backup_path = f'{config_path}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    print("🔧 MCP配置修复工具")
    print("=" * 50)
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        print(f"❌ 错误: MCP配置文件不存在: {config_path}")
        print("请确认Trae AI已正确安装并运行过。")
        return False
    
    try:
        # 备份原配置文件
        print(f"📋 创建配置备份: {backup_path}")
        shutil.copy2(config_path, backup_path)
        
        # 读取当前配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📖 读取当前MCP配置...")
        
        # 检查是否存在mcpServers配置
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        
        # 检查test-file-manager配置
        if 'test-file-manager' not in config['mcpServers']:
            print("➕ 添加test-file-manager服务器配置...")
            config['mcpServers']['test-file-manager'] = {
                "command": "node",
                "args": [
                    "/home/metaspeekoj/mcp-servers/test_file_manager_mcp_server.js"
                ],
                "cwd": "/home/metaspeekoj/mcp-servers",
                "env": {
                    "NODE_PATH": "/home/metaspeekoj/node_modules"
                }
            }
        else:
            # 检查并添加缺失的cwd参数
            test_manager_config = config['mcpServers']['test-file-manager']
            
            if 'cwd' not in test_manager_config:
                print("🔧 添加缺失的cwd参数...")
                test_manager_config['cwd'] = "/home/metaspeekoj/mcp-servers"
            else:
                print("✅ cwd参数已存在")
            
            # 确保其他必要参数存在
            if 'env' not in test_manager_config:
                test_manager_config['env'] = {}
            
            if 'NODE_PATH' not in test_manager_config['env']:
                test_manager_config['env']['NODE_PATH'] = "/home/metaspeekoj/node_modules"
        
        # 写入修复后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ MCP配置修复完成!")
        print("\n📋 修复后的test-file-manager配置:")
        print(json.dumps(config['mcpServers']['test-file-manager'], indent=2, ensure_ascii=False))
        
        print("\n🔄 请重启Trae AI或重新加载MCP配置以使更改生效。")
        
        return True
        
    except PermissionError:
        print(f"❌ 权限错误: 无法访问配置文件 {config_path}")
        print("请确保有足够的权限访问Trae AI配置目录。")
        return False
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print("配置文件格式可能已损坏，请检查备份文件。")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def show_current_status():
    """
    显示当前MCP服务器状态
    """
    print("\n📊 当前服务器状态:")
    print("-" * 30)
    
    # 检查服务器进程
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'test_file_manager_mcp_server.js' in result.stdout:
            print("✅ test-file-manager服务器正在运行")
        else:
            print("❌ test-file-manager服务器未运行")
    except:
        print("⚠️  无法检查服务器进程状态")
    
    # 检查TestCode目录
    testcode_dir = '/home/metaspeekoj/TestCode'
    if os.path.exists(testcode_dir):
        file_count = len([f for f in os.listdir(testcode_dir) if os.path.isfile(os.path.join(testcode_dir, f))])
        print(f"📁 TestCode目录存在，包含 {file_count} 个文件")
    else:
        print("📁 TestCode目录不存在")

def main():
    """
    主函数
    """
    print("🚀 MCP测试文件管理服务器配置修复工具")
    print("=" * 60)
    
    # 显示当前状态
    show_current_status()
    
    # 询问是否继续修复
    print("\n❓ 是否要修复MCP配置? (y/n): ", end='')
    
    # 在脚本环境中自动执行修复
    print("y")
    choice = 'y'
    
    if choice.lower() in ['y', 'yes', '是']:
        success = fix_mcp_config()
        if success:
            print("\n🎉 配置修复成功!")
            print("\n📝 后续步骤:")
            print("1. 重启Trae AI IDE")
            print("2. 或者重新加载MCP配置")
            print("3. 验证test-file-manager工具是否可用")
        else:
            print("\n❌ 配置修复失败，请查看上述错误信息")
    else:
        print("\n⏹️  操作已取消")
    
    print("\n📚 更多信息请查看: /home/metaspeekoj/mcp-servers/MCP_STARTUP_TROUBLESHOOTING.md")

if __name__ == '__main__':
    main()