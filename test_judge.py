#!/usr/bin/env python3

import requests
import json

# 测试判题服务器连接
def test_judge_server():
    url = "http://172.20.0.3:8080/judge"
    
    # 简单的测试数据
    test_data = {
        "language_config": {
            "compile": {
                "src_name": "main.cpp",
                "exe_name": "main",
                "max_cpu_time": 10000,
                "max_real_time": 20000,
                "max_memory": 1073741824,
                "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++20 {src_path} -lm -o {exe_path}"
            },
            "run": {
                "command": "{exe_path}",
                "seccomp_rule": {
                    "File IO": "c_cpp_file_io",
                    "Standard IO": "c_cpp"
                },
                "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
            }
        },
        "src": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
        "max_cpu_time": 1000,
        "max_memory": 268435456,
        "test_case_id": "test_case_1",
        "output": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Judge-Server-Token": "f977a4a1a2742839194c02f3e534f931c1ca13c4b3f303b1488e44703df0394c"
    }
    
    try:
        print(f"Testing judge server at: {url}")
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Judge result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Judge server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error connecting to judge server: {e}")
        return False

if __name__ == "__main__":
    test_judge_server()