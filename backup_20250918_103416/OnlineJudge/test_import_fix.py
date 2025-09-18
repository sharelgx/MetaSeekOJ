#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户提供的JSON数据导入功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

import json
from choice_question.import_serializers import ChoiceQuestionImportSerializer
from django.contrib.auth import get_user_model
from django.db import transaction

def test_import():
    """测试导入功能"""
    # 用户提供的JSON数据
    test_data = {
        "questions": [
            {
                "id": "GESP_2_2024_3_1",
                "type": "single",
                "question": "下列关于C++语言变量的叙述，正确的是( )｡E=mc²;∫(a到b) [f(x)·g'(x)]dx = f(b)g(b) - f(a)g(a) - ∫(a到b) [f'(x)·g(x)]dx",
                "options": [
                    "A. 变量可以没有定义",
                    "B. 对一个没有定义的变量赋值，相当于定义了一个新变量",
                    "C. 执行赋值语句后，变量的类型可能会变化",
                    "D. 执行赋值语句后，变量的值可能不会变化"
                ],
                "correct": "D",
                "explanation": "变量需先定义后使用（排除A、B），赋值不改变类型（排除C）。若赋值前后值相同，值不变（如a=5; a=5;），故D正确。"
            },
            {
                "id": "GESP_2_2024_3_2",
                "type": "single",
                "question": "<pre>\n#include<bits/stdc++.h>\nusing namespace std;\nint main() {\n    int n;\n    cin >> n;\n    for (int i = 1; i * i * i <= n; i++) {\n        if (i * i * i == n) {\n            cout << \"Yes\" << endl;\n            return 0;\n        }\n    }\n    cout << \"No\" << endl;\n    return 0;\n}\n</pre>",
                "options": [
                    "A. array[min] > array[j]",
                    "B. array[min] > array[i]",
                    "C. min > array[j]",
                    "D. min > array[i]"
                ],
                "correct": "A",
                "explanation": "本题属于考察选择排序算法；选择排序每次会从待排序的数据元素中选出最小的一个元素，存放在序列的起始位置，也就是对于所有的i+1<=j<n，找到最小的array[j]。"
            }
        ],
        "category_id": None
    }
    
    print("开始测试导入功能...")
    
    # 获取超级用户
    User = get_user_model()
    from account.models import AdminType
    superuser = User.objects.filter(admin_type=AdminType.SUPER_ADMIN).first()
    if not superuser:
        print("错误：未找到超级用户")
        return False
    
    print(f"找到超级用户：{superuser.username}")
    
    # 添加创建者信息
    test_data['created_by'] = superuser
    
    # 验证数据
    serializer = ChoiceQuestionImportSerializer(data=test_data)
    if serializer.is_valid():
        print("数据验证成功！")
        
        # 尝试创建
        try:
            with transaction.atomic():
                result = serializer.create(serializer.validated_data)
                print(f"导入成功！成功导入 {result['success_count']}/{result['total_count']} 道题目")
                if result['errors']:
                    print(f"错误列表：{result['errors']}")
                return True
        except Exception as e:
            print(f"创建失败：{str(e)}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"数据验证失败：{serializer.errors}")
        return False

if __name__ == '__main__':
    success = test_import()
    if success:
        print("\n测试通过！导入功能正常工作。")
    else:
        print("\n测试失败！请检查错误信息。")