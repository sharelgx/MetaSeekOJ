#!/usr/bin/env python3
"""
判题服务器心跳脚本
定期向后端发送心跳请求，保持判题服务器状态为normal
"""

import requests
import time
import json
import hashlib
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8086/api/judge_server_heartbeat/"
JUDGE_SERVER_TOKEN = "a1891f62363f80f6702ef77d50d1e91e"  # 原始token
HOSTNAME = "onlinejudgedeploy-oj-judge-1"
SERVICE_URL = "http://172.20.0.3:8080"
HEARTBEAT_INTERVAL = 5  # 每5秒发送一次心跳

def send_heartbeat():
    """发送心跳请求"""
    # 计算token的SHA256哈希
    hashed_token = hashlib.sha256(JUDGE_SERVER_TOKEN.encode('utf-8')).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Judge-Server-Token": hashed_token
    }
    
    data = {
        "hostname": HOSTNAME,
        "judger_version": "2.1.1",
        "cpu_core": 4,
        "memory": 0.5,
        "cpu": 0.1,
        "action": "heartbeat",
        "service_url": SERVICE_URL
    }
    
    try:
        response = requests.post(BACKEND_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("error") is None:
                print(f"[{datetime.now()}] 心跳发送成功")
                return True
            else:
                print(f"[{datetime.now()}] 心跳发送失败: {result.get('error')}")
                return False
        else:
            print(f"[{datetime.now()}] HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] 心跳发送异常: {e}")
        return False

def main():
    """主函数"""
    print(f"[{datetime.now()}] 启动判题服务器心跳服务")
    print(f"目标服务器: {HOSTNAME}")
    print(f"后端URL: {BACKEND_URL}")
    print(f"心跳间隔: {HEARTBEAT_INTERVAL}秒")
    print("-" * 50)
    
    while True:
        try:
            send_heartbeat()
            time.sleep(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] 收到中断信号，停止心跳服务")
            break
        except Exception as e:
            print(f"[{datetime.now()}] 未知错误: {e}")
            time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()