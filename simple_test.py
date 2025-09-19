import os
import subprocess

# 测试判题服务器连接
result = subprocess.run([
    'curl', '-X', 'POST', 'http://172.20.0.3:8080/judge',
    '-H', 'Content-Type: application/json',
    '-H', 'X-Judge-Server-Token: f977a4a1a2742839194c02f3e534f931c1ca13c4b3f303b1488e44703df0394c',
    '-d', '{"src":"#include <iostream>\\nint main(){return 0;}","language_config":{"compile":{"src_name":"main.cpp","exe_name":"main","compile_command":"/usr/bin/g++ {src_path} -o {exe_path}"}},"max_cpu_time":1000,"max_memory":268435456,"test_case_id":"test"}',
    '--connect-timeout', '10'
], capture_output=True, text=True)

with open('/home/metaspeekoj/test_result.txt', 'w') as f:
    f.write(f"Exit code: {result.returncode}\n")
    f.write(f"Stdout: {result.stdout}\n")
    f.write(f"Stderr: {result.stderr}\n")

print(f"Test completed. Exit code: {result.returncode}")
print(f"Output written to test_result.txt")