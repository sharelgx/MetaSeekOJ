#!/usr/bin/env python3
# 这是一个测试文件，用于验证自动检测功能

print("这是一个自动生成的测试文件")
print("应该被自动检测并移动到TestCode目录")

# 简单的测试函数
def test_function():
    return "测试成功"

if __name__ == "__main__":
    result = test_function()
    print(f"测试结果: {result}")