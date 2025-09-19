#!/usr/bin/env python3
import os
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import UserProfile
from django.contrib.auth.models import User

def fix_user_profiles():
    print("=== 修复用户配置文件数据格式 ===")
    
    # 获取所有用户配置
    profiles = UserProfile.objects.all()
    print(f"找到 {profiles.count()} 个用户配置:")
    
    fixed_count = 0
    for profile in profiles:
        try:
            # 检查acm_problems_status字段
            if isinstance(profile.acm_problems_status, str):
                try:
                    # 尝试解析JSON
                    acm_data = json.loads(profile.acm_problems_status)
                    print(f"用户 {profile.user.username}: acm_problems_status 已是有效JSON")
                except json.JSONDecodeError:
                    print(f"用户 {profile.user.username}: acm_problems_status JSON格式错误，重置为空字典")
                    profile.acm_problems_status = '{}'
                    profile.save()
                    fixed_count += 1
            
            # 检查oi_problems_status字段
            if isinstance(profile.oi_problems_status, str):
                try:
                    # 尝试解析JSON
                    oi_data = json.loads(profile.oi_problems_status)
                    print(f"用户 {profile.user.username}: oi_problems_status 已是有效JSON")
                except json.JSONDecodeError:
                    print(f"用户 {profile.user.username}: oi_problems_status JSON格式错误，重置为空字典")
                    profile.oi_problems_status = '{}'
                    profile.save()
                    fixed_count += 1
                    
        except Exception as e:
            print(f"处理用户 {profile.user.username} 时出错: {e}")
    
    print(f"\n修复完成，共修复 {fixed_count} 个配置")

def test_json_parsing():
    print("\n=== 测试JSON解析 ===")
    
    # 测试第一个用户的数据
    try:
        profile = UserProfile.objects.first()
        if profile:
            print(f"测试用户: {profile.user.username}")
            
            # 测试acm_problems_status
            acm_str = profile.acm_problems_status
            print(f"acm_problems_status 原始值: {acm_str}")
            print(f"类型: {type(acm_str)}")
            
            if isinstance(acm_str, str):
                try:
                    acm_data = json.loads(acm_str)
                    print(f"解析后的acm数据: {acm_data}")
                    print(f"获取problems: {acm_data.get('problems', {})}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
            
    except Exception as e:
        print(f"测试时出错: {e}")

if __name__ == '__main__':
    test_json_parsing()
    fix_user_profiles()