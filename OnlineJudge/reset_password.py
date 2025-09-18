#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User

# Reset root user password
try:
    user = User.objects.get(username='root')
    user.set_password('rootroot')
    user.save()
    print(f'Password for user "{user.username}" has been reset successfully.')
    
    # Test the new password
    from django.contrib.auth import authenticate
    test_user = authenticate(username='root', password='rootroot')
    if test_user:
        print('Password verification successful!')
    else:
        print('Password verification failed!')
        
except User.DoesNotExist:
    print('User "root" does not exist.')
except Exception as e:
    print(f'Error: {e}')