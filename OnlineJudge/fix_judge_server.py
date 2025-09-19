#!/usr/bin/env python3
import os
import django
import requests
import hashlib
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from conf.models import JudgeServer
from options.options import SysOptions

def fix_judge_server():
    print("=== 修复判题服务器状态 ===")
    
    # 获取判题服务器
    servers = JudgeServer.objects.all()
    print(f"找到 {servers.count()} 个判题服务器:")
    
    for server in servers:
        print(f"\n服务器: {server.hostname}")
        print(f"  URL: {server.service_url}")
        print(f"  当前状态: {server.status}")
        print(f"  是否禁用: {server.is_disabled}")
        
        # 测试连接
        try:
            # 获取token并计算哈希
            token = SysOptions.judge_server_token
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Judge-Server-Token': hashed_token
            }
            
            response = requests.post(f"{server.service_url}/ping", 
                                   json={}, 
                                   headers=headers, 
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('err') is None:
                    print(f"  连接测试: 成功")
                    print(f"  判题器版本: {data['data'].get('judger_version', 'unknown')}")
                    print(f"  CPU使用率: {data['data'].get('cpu', 0)}%")
                    print(f"  内存使用率: {data['data'].get('memory', 0)}%")
                    
                    # 更新服务器状态（通过更新last_heartbeat让status自动变为normal）
                    server.last_heartbeat = datetime.now()
                    server.cpu_usage = data['data'].get('cpu', 0)
                    server.memory_usage = data['data'].get('memory', 0)
                    server.save()
                    
                    print(f"  状态已更新，last_heartbeat: {server.last_heartbeat}")
                else:
                    print(f"  连接测试: 失败 - {data.get('err')}")
            else:
                print(f"  连接测试: 失败 - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  连接测试: 异常 - {e}")
    
    print("\n=== 修复完成 ===")
    
    # 再次检查状态
    servers = JudgeServer.objects.filter(is_disabled=False)
    print(f"\n可用判题服务器: {servers.count()}")
    for server in servers:
        print(f"  {server.hostname}: {server.status}")

if __name__ == '__main__':
    fix_judge_server()