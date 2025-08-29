# -*- coding: utf-8 -*-
"""
选择题插件入口文件
定义插件信息、安装和卸载函数
"""

PLUGIN_INFO = {
    "name": "choice-question",
    "version": "1.0.0",
    "display_name": "选择题插件",
    "description": "为OJ系统提供选择题功能的插件",
    "author": "QDU OJ Team",
    "license": "MIT",
    "homepage": "https://github.com/qdu-rm-lab/qduoj-choice-question-plugin",
    "dependencies": {
        "django": ">=3.2",
        "django-mptt": ">=0.13",
        "djangorestframework": ">=3.12"
    },
    "api_mount_point": "/api/plugin/choice/",
    "frontend_routes": ["/choice/*"],
    "menu_items": [
        {
            "title": "选择题",
            "icon": "question-circle",
            "path": "/choice",
            "permission": "choice_question.view_choicequestion"
        }
    ],
    "permissions": [
        "choice_question.view_choicequestion",
        "choice_question.add_choicequestion",
        "choice_question.change_choicequestion",
        "choice_question.delete_choicequestion",
        "choice_question.view_category",
        "choice_question.add_category",
        "choice_question.change_category",
        "choice_question.delete_category"
    ]
}


def install():
    """
    插件安装入口
    执行数据库迁移和初始化数据
    """
    try:
        from django.core.management import execute_from_command_line
        import os
        import sys
        
        # 执行数据库迁移
        print("正在执行数据库迁移...")
        execute_from_command_line(['manage.py', 'migrate', 'choice_question'])
        
        # 创建默认分类
        print("正在创建默认分类...")
        from choice_question.models import Category
        default_category, created = Category.objects.get_or_create(
            name="默认分类",
            defaults={
                "description": "默认选择题分类",
                "is_active": True
            }
        )
        
        if created:
            print(f"已创建默认分类: {default_category.name}")
        else:
            print(f"默认分类已存在: {default_category.name}")
            
        print("插件安装完成!")
        return True
        
    except Exception as e:
        print(f"插件安装失败: {str(e)}")
        return False


def uninstall():
    """
    插件卸载入口
    清理数据库表和相关数据
    """
    try:
        from django.core.management import execute_from_command_line
        
        print("正在卸载插件...")
        
        # 警告用户数据将被删除
        print("警告: 卸载插件将删除所有选择题相关数据!")
        
        # 回滚数据库迁移
        execute_from_command_line(['manage.py', 'migrate', 'choice_question', 'zero'])
        
        print("插件卸载完成!")
        return True
        
    except Exception as e:
        print(f"插件卸载失败: {str(e)}")
        return False


def get_info():
    """
    获取插件信息
    """
    return PLUGIN_INFO


def get_version():
    """
    获取插件版本
    """
    return PLUGIN_INFO["version"]


def is_compatible(oj_version):
    """
    检查插件与OJ系统的兼容性
    """
    # 这里可以添加版本兼容性检查逻辑
    return True


def get_api_urls():
    """
    获取插件API路由
    """
    from choice_question.urls import urlpatterns
    return urlpatterns


def get_admin_urls():
    """
    获取插件管理后台路由
    """
    from choice_question.admin import admin_site
    return admin_site.urls if hasattr(admin_site, 'urls') else []