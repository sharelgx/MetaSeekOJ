#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import hashlib

def test_judge_server():
    # 判题服务器配置
    judge_server_url = "http://172.20.0.3:8080"
    token = "a1891f62363f80f6702ef77d50d1e91e"  # 从数据库获取的token
    
    print(f"测试判题服务器: {judge_server_url}")
    
    # 测试ping接口
    try:
        ping_url = f"{judge_server_url}/ping"
        headers = {
            "Content-Type": "application/json",
            "X-Judge-Server-Token": hashlib.sha256(token.encode()).hexdigest()
        }
        
        response = requests.post(ping_url, json={}, headers=headers, timeout=5)
        print(f"Ping响应状态码: {response.status_code}")
        print(f"Ping响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"服务器状态: {data}")
        
    except Exception as e:
        print(f"Ping测试失败: {e}")
    
    # 测试简单的判题请求
    try:
        judge_url = f"{judge_server_url}/judge"
        
        test_data = {
            "language_config": {
                "src_name": "main.c",
                "exe_name": "main",
                "compile": {
                    "src_name": "main.c",
                    "exe_name": "main",
                    "max_cpu_time": 3000,
                    "max_real_time": 5000,
                    "max_memory": 134217728,
                    "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}"
                },
                "run": {
                    "command": "{exe_path}",
                    "seccomp_rule": "c_cpp",
                    "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
                }
            },
            "src": "#include <stdio.h>\nint main() {\n    printf(\"Hello World\\n\");\n    return 0;\n}",
            "max_cpu_time": 1000,
            "max_memory": 134217728,
            "test_case_id": "test",
            "output": True
        }
        
        response = requests.post(judge_url, json=test_data, headers=headers, timeout=10)
        print(f"\n判题响应状态码: {response.status_code}")
        print(f"判题响应内容: {response.text}")
        
    except Exception as e:
        print(f"判题测试失败: {e}")

if __name__ == '__main__':
    test_judge_server()