#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from account.views.oj import SessionManagementAPI
from django.contrib.sessions.backends.db import SessionStore

User = get_user_model()

try:
    # Get the root user
    user = User.objects.get(username='root')
    print(f"User session_keys type: {type(user.session_keys)}")
    print(f"User session_keys value: {repr(user.session_keys)}")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/sessions')
    request.user = user
    
    # Create a session
    session = SessionStore()
    session.create()
    request.session = session
    
    # Test the API
    api = SessionManagementAPI()
    response = api.get(request)
    print(f"API Response: {response.data}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()