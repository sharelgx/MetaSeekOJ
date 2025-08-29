# 简化的Django测试设置
import os

# 基本设置
SECRET_KEY = 'test-secret-key-for-testing-only'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 数据库设置（使用内存SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 应用配置
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'mptt',
    'account',
    'choice_question',
]

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# 根URL配置
ROOT_URLCONF = 'test_urls'

# 时区设置
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'

# 用户模型
AUTH_USER_MODEL = 'account.User'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 测试设置
TESTING = True
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]