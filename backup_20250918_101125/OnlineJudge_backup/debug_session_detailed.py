import os
import django
import json
from importlib import import_module

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.conf import settings
from account.models import User
from django.contrib.sessions.backends.db import SessionStore

# 获取root用户
user = User.objects.get(username='root')
print(f"User session_keys type: {type(user.session_keys)}")
print(f"User session_keys value: {repr(user.session_keys)}")

# 解析session_keys
session_keys = user.session_keys
if isinstance(session_keys, str):
    try:
        session_keys = json.loads(session_keys)
        print(f"Parsed session_keys: {session_keys}")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Failed to parse session_keys: {e}")
        session_keys = []
elif session_keys is None:
    session_keys = []

print(f"Final session_keys: {session_keys}")

# 检查每个session
session_store = import_module(settings.SESSION_ENGINE).SessionStore
for key in session_keys:
    print(f"\nChecking session key: {key}")
    session = session_store(key)
    print(f"Session exists: {bool(session._session)}")
    if session._session:
        print(f"Session data: {dict(session._session)}")
        print(f"Session keys: {list(session._session.keys())}")
        if 'ip' in session:
            print(f"IP: {session['ip']}")
        if 'user_agent' in session:
            print(f"User Agent: {session['user_agent']}")
        if 'last_activity' in session:
            print(f"Last Activity: {session['last_activity']} (type: {type(session['last_activity'])})")
    else:
        print("Session is empty or expired")