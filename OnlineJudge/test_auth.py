#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User
from django.contrib.auth import authenticate

# Test authentication
print("Testing root user authentication...")
user = authenticate(username='root', password='rootroot')
print(f'Authentication result: {user}')
if user:
    print(f'User authenticated: {user.username}')
    print(f'User is active: {user.is_active}')
    print(f'User is staff: {user.is_staff}')
    print(f'User is superuser: {user.is_superuser}')
else:
    print('Authentication failed')
    # Try to check if user exists
    try:
        user_obj = User.objects.get(username='root')
        print(f'User exists: {user_obj.username}')
        print(f'User is active: {user_obj.is_active}')
        # Test password check
        from django.contrib.auth.hashers import check_password
        password_valid = check_password('rootroot', user_obj.password)
        print(f'Password check result: {password_valid}')
    except User.DoesNotExist:
        print('User does not exist')