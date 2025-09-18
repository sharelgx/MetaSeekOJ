#!/usr/bin/env python3
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db import transaction

print("=== 检查选择题相关表 ===")

with connection.cursor() as cursor:
    # 检查现有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%choice%';")
    tables = cursor.fetchall()
    print(f"现有选择题相关表: {[table[0] for table in tables]}")
    
    # 删除所有选择题相关表
    choice_tables = [
        'choice_plugin_category',
        'choice_plugin_question', 
        'choice_plugin_submission',
        'choice_plugin_tag',
        'choice_plugin_wrong',
        'choice_question_category',
        'choice_question',
        'choice_question_submission', 
        'choice_question_tag',
        'choice_question_wrong',
        'choice_question_choicequestion_tags',
        'choice_question_tags'  # 添加这个表
    ]
    
    for table in choice_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"删除表: {table}")
        except Exception as e:
            print(f"删除表 {table} 失败: {e}")
    
    # 删除迁移记录
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'choice_question';")
        print("删除choice_question迁移记录")
    except Exception as e:
        print(f"删除迁移记录失败: {e}")

print("\n=== 数据库清理完成 ===")