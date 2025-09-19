#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统状态检查脚本
用于检查青岛OJ系统各个组件的运行状态
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

def check_process(process_name):
    """检查进程是否运行"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name], 
                              capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0

def check_port(port):
    """检查端口是否被占用"""
    try:
        result = subprocess.run(['netstat', '-tlnp'], 
                              capture_output=True, text=True)
        return f':{port}' in result.stdout
    except:
        return False

def check_url(url, timeout=5):
    """检查URL是否可访问"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def check_database():
    """检查数据库连接"""
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        return True
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print(f"青岛OJ系统状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查环境变量
    print("\n📋 环境配置:")
    print(f"  OJ_ENV: {os.environ.get('OJ_ENV', '未设置')}")
    print(f"  OJ_DOCKER: {os.environ.get('OJ_DOCKER', '未设置')}")
    
    # 检查进程
    print("\n🔄 运行进程:")
    django_processes = check_process('runserver')
    dramatiq_processes = check_process('rundramatiq')
    npm_processes = check_process('npm run dev')
    
    print(f"  Django服务器: {django_processes} 个进程")
    print(f"  Dramatiq队列: {dramatiq_processes} 个进程")
    print(f"  前端服务: {npm_processes} 个进程")
    
    # 检查端口
    print("\n🌐 端口状态:")
    ports = [8000, 8080, 8086, 8087]
    for port in ports:
        status = "✅ 占用" if check_port(port) else "❌ 空闲"
        print(f"  端口 {port}: {status}")
    
    # 检查服务可访问性
    print("\n🔗 服务可访问性:")
    services = [
        ('前端服务', 'http://localhost:8080'),
        ('后端API (8086)', 'http://localhost:8086/api/website'),
        ('后端API (8000)', 'http://localhost:8000/api/website'),
    ]
    
    for name, url in services:
        status = "✅ 正常" if check_url(url) else "❌ 异常"
        print(f"  {name}: {status}")
    
    # 检查数据库
    print("\n💾 数据库状态:")
    try:
        db_result = check_database()
        if db_result is True:
            print("  数据库连接: ✅ 正常")
        else:
            print(f"  数据库连接: ❌ 异常 - {db_result[1]}")
    except Exception as e:
        print(f"  数据库连接: ❌ 检查失败 - {str(e)}")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == '__main__':
    main()