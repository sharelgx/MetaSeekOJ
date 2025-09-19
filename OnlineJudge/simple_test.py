#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from submission.models import Submission
from problem.models import Problem
from account.models import User
from judge.dispatcher import JudgeDispatcher

def create_simple_test():
    print("=== 创建简单测试提交 ===")
    
    # 获取第一个题目和用户
    problem = Problem.objects.first()
    user = User.objects.first()
    
    if not problem or not user:
        print("没有找到题目或用户")
        return
    
    print(f"题目: {problem.title}")
    print(f"用户: {user.username}")
    
    # 简单的C代码
    test_code = '''
#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\\n", a + b);
    return 0;
}
'''
    
    # 创建提交记录
    submission = Submission.objects.create(
        problem=problem,
        user_id=user.id,
        username=user.username,
        code=test_code,
        language="C"
    )
    
    print(f"提交ID: {submission.id}")
    print(f"初始状态: {submission.result}")
    
    # 触发判题
    try:
        JudgeDispatcher(submission.id, problem.id).judge()
        print("判题任务已提交")
        
        # 重新获取提交记录
        submission.refresh_from_db()
        print(f"判题后状态: {submission.result}")
        
        if submission.result != 6:  # 6表示正在判题
            print(f"判题完成，结果: {submission.result}")
            if hasattr(submission, 'statistic_info'):
                print(f"统计信息: {submission.statistic_info}")
            if hasattr(submission, 'info'):
                print(f"详细信息: {submission.info}")
        else:
            print("判题仍在进行中...")
            
    except Exception as e:
        print(f"判题出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_simple_test()