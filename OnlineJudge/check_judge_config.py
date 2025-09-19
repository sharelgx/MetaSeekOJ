#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from conf.models import JudgeServer
from options.options import SysOptions

print('Judge Servers:')
for server in JudgeServer.objects.all():
    print(f'ID: {server.id}')
    print(f'Hostname: {server.hostname}')
    print(f'IP: {server.ip}')
    print(f'Service URL: {server.service_url}')
    print(f'Status: {server.status}')
    print(f'Disabled: {server.is_disabled}')
    print(f'Last Heartbeat: {server.last_heartbeat}')
    print('---')

print('\nJudge Server Token:')
print(SysOptions.judge_server_token)