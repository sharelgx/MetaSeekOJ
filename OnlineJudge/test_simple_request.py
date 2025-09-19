#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

def test_simple_request():
    # 测试基本连接
    url = "http://localhost:12358/ping"
    headers = {"X-Judge-Server-Token": "f977a4a1a2742839194c02f3e534f931c1ca13c4b3f303b1488e44703df0394c"}
    
    print(f"测试URL: {url}")
    print(f"请求头: {headers}")
    
    try:
        # 尝试POST请求
        response = requests.post(url, headers=headers, timeout=10)
        print(f"POST响应状态码: {response.status_code}")
        print(f"POST响应头: {dict(response.headers)}")
        print(f"POST响应内容: {response.text}")
        
        # 尝试GET请求
        response = requests.get(url, headers=headers, timeout=10)
        print(f"GET响应状态码: {response.status_code}")
        print(f"GET响应头: {dict(response.headers)}")
        print(f"GET响应内容: {response.text}")
        
    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_request()