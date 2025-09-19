#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from submission.models import Submission
from problem.models import Problem
from account.models import User
from judge.dispatcher import JudgeDispatcher
from options.options import SysOptions

def test_judge_system():
    print("=== 测试判题系统 ===")
    
    # 1. 检查判题服务器配置
    print(f"判题服务器Token: {SysOptions.judge_server_token}")
    
    # 2. 检查判题服务器状态
    from conf.models import JudgeServer
    judge_servers = JudgeServer.objects.all()
    print(f"\n判题服务器列表:")
    for js in judge_servers:
        print(f"  ID: {js.id}, URL: {js.service_url}, IP: {js.ip}, 状态: {js.status}")
    
    # 3. 检查是否有可用题目
    problems = Problem.objects.filter(visible=True)[:5]
    print(f"\n可用题目数量: {problems.count()}")
    for p in problems:
        print(f"  题目ID: {p.id}, 标题: {p.title}")
    
    # 4. 检查是否有用户
    users = User.objects.all()
    print(f"\n用户数量: {users.count()}")
    for u in users[:3]:
        print(f"  用户: {u.username}, 管理员: {u.is_admin_role()}")
    
    # 5. 创建一个测试提交
    if problems.exists() and users.exists():
        problem = problems.first()
        user = users.first()
        
        # 简单的A+B问题代码
        test_code = '''#include <stdio.h>
int main(){
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}'''
        
        print(f"\n创建测试提交...")
        print(f"题目: {problem.title}")
        print(f"用户: {user.username}")
        print(f"代码长度: {len(test_code)} 字符")
        
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
            
            # 刷新提交状态
            submission.refresh_from_db()
            print(f"判题后状态: {submission.result}")
            
            if submission.result != -2:  # -2 表示等待判题
                print(f"CPU时间: {submission.cpu_time}ms")
                print(f"内存使用: {submission.memory}KB")
                if submission.info:
                    print(f"详细信息: {submission.info}")
            
        except Exception as e:
            print(f"判题出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    else:
        print("\n缺少题目或用户，无法创建测试提交")

if __name__ == "__main__":
    test_judge_system()