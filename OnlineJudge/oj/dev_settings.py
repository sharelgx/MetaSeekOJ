# coding=utf-8
import os
from utils.shortcuts import get_env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

REDIS_CONF = {
    'host': get_env('REDIS_HOST', '127.0.0.1'),
    'port': get_env('REDIS_PORT', '6379')
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
    'http://127.0.0.1:8081'
]

DATA_DIR = f"{BASE_DIR}/data"

# Session configuration to prevent timeout issues
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database sessions
