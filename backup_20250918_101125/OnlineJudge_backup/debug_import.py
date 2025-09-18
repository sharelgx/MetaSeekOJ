#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

import json
from choice_question.utils.importer import QuestionImporter

def debug_import():
    print("开始调试导入功能...")
    
    # 读取JSON文件
    with open('/home/metaspeekoj/TestCode/导入模板.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"原始数据: {data[0]}")
    
    # 创建导入器
    importer = QuestionImporter()
    
    try:
        # 测试格式转换
        converted = importer._convert_json_question_format(data[0], 1)
        print(f"转换后数据: {converted}")
        
        # 测试验证
        validation_result = importer.validator.validate_question_data(converted)
        print(f"验证结果: {validation_result}")
        
        # 如果验证通过，测试导入
        if validation_result['is_valid']:
            print("验证通过，尝试导入...")
            importer._import_single_question(converted)
            print("导入成功！")
        else:
            print(f"验证失败: {validation_result['errors']}")
            
    except Exception as e:
        import traceback
        print(f"发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")

if __name__ == '__main__':
    debug_import()