#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.utils.importer import QuestionImporter
from account.models import User

def test_batch_import():
    print("开始测试批量导入功能...")
    
    # 获取管理员用户
    try:
        user = User.objects.filter(admin_type='Super Admin').first()
        if not user:
            user = User.objects.first()  # 如果没有超级管理员，使用第一个用户
            if not user:
                print("未找到任何用户")
                return
        print(f"使用用户: {user.username}")
    except Exception as e:
        print(f"获取用户失败: {e}")
        return
    
    # 创建导入器
    importer = QuestionImporter(user=user)
    
    # 执行导入
    try:
        result = importer.import_from_json('/home/metaspeekoj/TestCode/导入模板.json')
        print("导入结果:")
        print(f"  成功数量: {result['success_count']}")
        print(f"  错误数量: {result['error_count']}")
        print(f"  总数量: {result['total_count']}")
        
        if result['error_count'] > 0:
            print("有错误发生，详情请查看日志")
        
        if result['logs']:
            print("导入日志:")
            for log in result['logs']:
                print(f"  {log}")
                
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_batch_import()