#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件创建功能演示
这个文件演示了新的create_test_file功能
确保所有测试文件都在TestCode目录下创建
"""

import unittest
import os

class TestNewFeatureDemo(unittest.TestCase):
    """演示新功能的测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.test_dir = '/home/metaspeekoj/TestCode'
        
    def test_file_location(self):
        """测试文件是否在正确的目录中"""
        current_file = os.path.abspath(__file__)
        self.assertTrue(current_file.startswith(self.test_dir))
        print(f"✅ 文件位置正确: {current_file}")
        
    def test_directory_exists(self):
        """测试TestCode目录是否存在"""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.isdir(self.test_dir))
        print(f"✅ TestCode目录存在: {self.test_dir}")
        
    def test_file_naming_convention(self):
        """测试文件命名规范"""
        filename = os.path.basename(__file__)
        self.assertTrue(filename.startswith('test_'))
        self.assertTrue(filename.endswith('.py'))
        print(f"✅ 文件命名符合规范: {filename}")

if __name__ == '__main__':
    print("=== 测试文件创建功能演示 ===")
    print(f"当前文件: {__file__}")
    print(f"文件目录: {os.path.dirname(__file__)}")
    print("\n开始运行测试...")
    
    unittest.main(verbosity=2)