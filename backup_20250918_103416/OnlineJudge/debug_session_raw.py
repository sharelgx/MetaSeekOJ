import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User

# 获取root用户
user = User.objects.get(username='root')
raw_value = user.session_keys
print('Raw value:', repr(raw_value))
print('Length:', len(raw_value))
print('First 10 chars:', repr(raw_value[:10]))
print('Last 10 chars:', repr(raw_value[-10:]))

# 尝试不同的解析方法
import json
import ast

print('\n--- Trying json.loads ---')
try:
    result = json.loads(raw_value)
    print('Success:', result)
except Exception as e:
    print('Failed:', e)

print('\n--- Trying ast.literal_eval ---')
try:
    result = ast.literal_eval(raw_value)
    print('Success:', result)
except Exception as e:
    print('Failed:', e)

print('\n--- Trying eval (unsafe but for debugging) ---')
try:
    result = eval(raw_value)
    print('Success:', result)
except Exception as e:
    print('Failed:', e)