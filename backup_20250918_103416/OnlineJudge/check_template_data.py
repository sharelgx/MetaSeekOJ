#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.models import Problem

# 检查Problem表中template字段的数据类型和内容
problems = Problem.objects.all()[:5]  # 只检查前5个

print(f"Problem总数: {Problem.objects.count()}")
print("\n检查template字段:")

for problem in problems:
    print(f"\nProblem ID: {problem.id}, _id: {problem._id}")
    print(f"Template类型: {type(problem.template)}")
    print(f"Template内容: {repr(problem.template)}")
    
    # 如果template是字符串，尝试解析
    if isinstance(problem.template, str):
        print("⚠️  Template是字符串类型，应该是JSON对象")
        try:
            import json
            parsed = json.loads(problem.template)
            print(f"解析后的内容: {parsed}")
        except Exception as e:
            print(f"解析失败: {e}")
    elif isinstance(problem.template, dict):
        print("✓ Template是字典类型，正常")
    else:
        print(f"❌ Template是未知类型: {type(problem.template)}")