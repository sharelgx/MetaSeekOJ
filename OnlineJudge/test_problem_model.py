#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.models import Problem
from account.models import User

print("=== 测试Problem模型的visible字段操作 ===")

try:
    # 获取题目259测试
    problem = Problem.objects.filter(id=259).first()
    if problem:
        print(f"题目ID: {problem.id}")
        print(f"题目标题: {problem.title}")
        print(f"修改前visible状态: {problem.visible}")
        print(f"visible字段类型: {type(problem.visible)}")
        
        # 尝试直接修改为True
        original_visible = problem.visible
        problem.visible = True
        problem.save()
        
        # 重新从数据库获取验证
        problem.refresh_from_db()
        print(f"修改后visible状态: {problem.visible}")
        print(f"修改是否成功: {problem.visible == True}")
        
        # 再次修改为False测试
        problem.visible = False
        problem.save()
        problem.refresh_from_db()
        print(f"修改为False后状态: {problem.visible}")
        
        # 恢复原始状态
        problem.visible = original_visible
        problem.save()
        print(f"恢复原始状态: {problem.visible}")
        
    else:
        print("❌ 题目259不存在")
        
except Exception as e:
    print(f"❌ 测试时出错: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 检查Problem模型的visible字段定义 ===")
try:
    visible_field = Problem._meta.get_field('visible')
    print(f"字段类型: {type(visible_field)}")
    print(f"字段名称: {visible_field.name}")
    print(f"默认值: {visible_field.default}")
    print(f"是否允许null: {visible_field.null}")
    print(f"是否允许blank: {visible_field.blank}")
except Exception as e:
    print(f"❌ 检查字段定义时出错: {e}")

print("\n=== 测试批量更新 ===")
try:
    # 测试批量更新是否正常工作
    test_problems = Problem.objects.filter(id__in=[1, 2, 3])[:2]
    print(f"测试题目数量: {test_problems.count()}")
    
    for p in test_problems:
        print(f"题目{p.id}修改前: {p.visible}")
    
    # 批量设置为True
    Problem.objects.filter(id__in=[p.id for p in test_problems]).update(visible=True)
    
    # 重新查询验证
    updated_problems = Problem.objects.filter(id__in=[p.id for p in test_problems])
    for p in updated_problems:
        print(f"题目{p.id}批量修改后: {p.visible}")
        
except Exception as e:
    print(f"❌ 批量更新测试时出错: {e}")