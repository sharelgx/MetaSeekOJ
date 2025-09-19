#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作区索引测试脚本
用于验证IDE索引功能是否正常工作
"""

import os
import sys
from datetime import datetime

def test_file_access():
    """测试文件访问权限"""
    test_dirs = [
        '/home/metaspeekoj/OnlineJudge',
        '/home/metaspeekoj/OnlineJudgeFE', 
        '/home/metaspeekoj/开发文档'
    ]
    
    results = []
    for dir_path in test_dirs:
        try:
            if os.path.exists(dir_path) and os.access(dir_path, os.R_OK):
                file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
                results.append(f"✓ {dir_path}: 可访问，包含 {file_count} 个文件")
            else:
                results.append(f"✗ {dir_path}: 无法访问")
        except Exception as e:
            results.append(f"✗ {dir_path}: 错误 - {str(e)}")
    
    return results

def test_vscode_settings():
    """测试VSCode设置"""
    settings_path = '/home/metaspeekoj/.vscode/settings.json'
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"Codegeex.RepoIndex": false' in content:
                return "✓ CodeGeeX仓库索引已禁用"
            else:
                return "✗ CodeGeeX仓库索引仍然启用"
    except Exception as e:
        return f"✗ 无法读取VSCode设置: {str(e)}"

def main():
    print("=== 工作区索引测试报告 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1. 文件访问测试:")
    access_results = test_file_access()
    for result in access_results:
        print(f"   {result}")
    print()
    
    print("2. VSCode设置测试:")
    settings_result = test_vscode_settings()
    print(f"   {settings_result}")
    print()
    
    print("3. 系统信息:")
    print(f"   当前用户: {os.getenv('USER', 'unknown')}")
    print(f"   当前工作目录: {os.getcwd()}")
    print(f"   Python版本: {sys.version.split()[0]}")
    print()
    
    print("=== 测试完成 ===")
    print("如果所有测试都显示 ✓，说明工作区索引问题已解决")
    print("如果仍有问题，请检查IDE是否需要重启")

if __name__ == '__main__':
    main()