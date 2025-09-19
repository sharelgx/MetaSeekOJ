# coding=utf-8
# Docker环境数据库配置文件
# 用于连接Docker容器中的PostgreSQL数据库

from utils.shortcuts import get_env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '172.17.0.3',  # Docker PostgreSQL容器IP
        'PORT': '5432',
        'NAME': 'onlinejudge',
        'USER': 'onlinejudge',
        'PASSWORD': 'onlinejudge'
    }
}

REDIS_CONF = {
    'host': '172.17.0.2',  # Docker Redis IP
    'port': '6379'
}

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CSRF trusted origins for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8081',
    'http://127.0.0.1:8081',
    'http://localhost:8086',
    'http://127.0.0.1:8086'
]

# 使用本地数据目录
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = f"{BASE_DIR}/data"

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'