#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamPaper, Category, ChoiceQuestion
from choice_question.api.topic.topic_practice import TopicPracticeDetailAPI
from django.http import HttpRequest
from django.test import RequestFactory

# 创建模拟请求
factory = RequestFactory()
request = factory.get('/api/topic/practice/4/')

# 创建API实例
api = TopicPracticeDetailAPI()

print('=== 完整API测试 ===')
print('测试分类ID: 4')

try:
    # 直接调用API的get方法
    response = api.get(request, category_id=4)
    
    print(f'API响应状态: {response.status_code}')
    print(f'API响应数据类型: {type(response.data)}')
    
    if hasattr(response, 'data') and response.data:
        data = response.data
        print(f'响应数据键: {list(data.keys()) if isinstance(data, dict) else "非字典类型"}')
        
        if isinstance(data, dict):
            if 'data' in data:
                inner_data = data['data']
                print(f'内部数据键: {list(inner_data.keys()) if isinstance(inner_data, dict) else "非字典类型"}')
                
                if isinstance(inner_data, dict):
                    print(f'exam_papers数量: {len(inner_data.get("exam_papers", []))}')
                    print(f'child_categories数量: {len(inner_data.get("child_categories", []))}')
                    print(f'questions数量: {len(inner_data.get("questions", []))}')
                    
                    # 显示exam_papers的详细信息
                    exam_papers = inner_data.get('exam_papers', [])
                    if exam_papers:
                        print('\n=== exam_papers详情 ===')
                        for i, paper in enumerate(exam_papers[:3]):
                            print(f'试卷{i+1}: {paper}')
                    else:
                        print('\n!!! exam_papers为空 !!!')
            else:
                print('响应数据中没有"data"键')
        else:
            print('响应数据不是字典格式')
    else:
        print('API响应没有数据')
        
except Exception as e:
    print(f'API调用出错: {e}')
    import traceback
    traceback.print_exc()