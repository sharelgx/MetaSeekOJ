#!/usr/bin/env python3
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.models import Problem
from account.models import User

try:
    problem = Problem.objects.get(id=268)
    print(f'Problem ID: {problem.id}')
    print(f'Problem Title: {problem.title}')
    print(f'Created by: {problem.created_by.username if problem.created_by else None}')
    print(f'Visible: {problem.visible}')
    print(f'Is Public: {problem.is_public}')
except Problem.DoesNotExist:
    print('Problem 268 does not exist')
    # 查看所有问题的ID范围
    problems = Problem.objects.all().order_by('id')
    if problems.exists():
        print(f'Available problem IDs range from {problems.first().id} to {problems.last().id}')
        print(f'Total problems: {problems.count()}')
    else:
        print('No problems found in database')
except Exception as e:
    print(f'Error: {e}')