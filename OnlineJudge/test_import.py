#!/usr/bin/env python3
import os
import sys
import django

# 添加项目路径
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineJudge.settings')
django.setup()

from choice_question.import_serializers import ChoiceQuestionImportSerializer
from account.models import User
from choice_question.models import ChoiceQuestion

def test_import():
    # 获取管理员用户
    admin_user = User.objects.filter(admin_type='Super Admin').first()
    if not admin_user:
        print('未找到管理员用户')
        return
    
    print(f'找到管理员用户: {admin_user.username}')
    
    # 记录导入前的题目数量
    before_count = ChoiceQuestion.objects.count()
    print(f'导入前题目数量: {before_count}')
    
    # 测试数据
    test_data = {
        'questions': [
            {
                'id': 'GESP_2_2024_3_1',
                'type': 'single',
                'question': '下列关于C++语言变量的叙述，正确的是( )｡',
                'options': [
                    'A. 变量可以没有定义',
                    'B. 对一个没有定义的变量赋值，相当于定义了一个新变量',
                    'C. 执行赋值语句后，变量的类型可能会变化',
                    'D. 执行赋值语句后，变量的值可能不会变化'
                ],
                'correct': 'D',
                'explanation': '变量需先定义后使用（排除A、B），赋值不改变类型（排除C）。若赋值前后值相同，值不变（如a=5; a=5;），故D正确。'
            },
            {
                'id': 'GESP_2_2024_3_2',
                'type': 'single',
                'question': '代码执行完结果是：',
                'options': [
                    'A. array[min] > array[j]',
                    'B. array[min] > array[i]',
                    'C. min > array[j]',
                    'D. min > array[i]'
                ],
                'correct': 'A',
                'explanation': '本题属于考察选择排序算法；选择排序每次会从待排序的数据元素中选出最小的一个元素，存放在序列的起始位置，也就是对于所有的i+1<=j<n，找到最小的array[j]。'
            }
        ]
    }
    
    # 测试序列化器
    print('开始测试导入...')
    serializer = ChoiceQuestionImportSerializer(data=test_data, context={'request_user': admin_user})
    
    if serializer.is_valid():
        print('验证成功！')
        try:
            result = serializer.save()
            print(f'导入结果: {result}')
            
            # 检查导入后的题目数量
            after_count = ChoiceQuestion.objects.count()
            print(f'导入后题目数量: {after_count}')
            print(f'新增题目数量: {after_count - before_count}')
            
            # 查看最新的几道题目
            latest_questions = ChoiceQuestion.objects.order_by('-id')[:3]
            print('\n最新的题目:')
            for q in latest_questions:
                print(f'ID: {q.id}, 标题: {q.title}, 描述: {q.description[:50]}..., 可见: {q.visible}')
                
        except Exception as e:
            print(f'保存时出错: {e}')
            import traceback
            traceback.print_exc()
    else:
        print('验证失败:')
        print(serializer.errors)

if __name__ == '__main__':
    test_import()