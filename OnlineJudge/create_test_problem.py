#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.models import Problem
from account.models import User

def create_test_problem():
    # 获取或创建管理员用户
    admin_user = User.objects.filter(is_super_admin=True).first()
    if not admin_user:
        admin_user = User.objects.create(
            username='admin',
            email='admin@test.com',
            is_super_admin=True
        )
        print(f'创建管理员用户: {admin_user.username}')
    
    # 创建测试题目
    problem = Problem.objects.create(
        title='A+B Problem',
        description='计算两个整数的和',
        input_description='两个整数a和b',
        output_description='输出a+b的结果',
        time_limit=1000,
        memory_limit=256,
        difficulty='Low',
        created_by=admin_user,
        test_case_score=[{'score': 100}],
        samples=[{'input': '1 2', 'output': '3'}]
    )
    
    print(f'创建题目ID: {problem.id}, 标题: {problem.title}')
    return problem.id

if __name__ == '__main__':
    problem_id = create_test_problem()
    print(f'测试题目创建完成，ID: {problem_id}')
