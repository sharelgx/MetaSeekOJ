#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from conf.models import JudgeServer

# 更新判题服务器的service_url
try:
    judge_server = JudgeServer.objects.get(id=1)
    old_url = judge_server.service_url
    judge_server.service_url = 'http://172.20.0.3:8080'
    judge_server.save()
    print(f'Updated judge server service_url from {old_url} to {judge_server.service_url}')
except JudgeServer.DoesNotExist:
    print('Judge server with ID 1 not found')
except Exception as e:
    print(f'Error updating judge server: {e}')