# Mock account.decorators for testing
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def login_required(func):
    """Mock login_required decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[1] if len(args) > 1 else None
        if not request or not request.user.is_authenticated:
            return Response({"error": "permission-denied", "data": "Please login first"}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        return func(*args, **kwargs)
    return wrapper

def super_admin_required(func):
    """Mock super_admin_required decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[1] if len(args) > 1 else None
        if not request or not request.user.is_authenticated:
            return Response({"error": "permission-denied", "data": "Please login first"}, 
                          status=status.HTTP_403_FORBIDDEN)
        if not (request.user.is_staff and request.user.is_superuser):
            return Response({"error": "permission-denied", "data": "Super admin required"}, 
                          status=status.HTTP_403_FORBIDDEN)
        return func(*args, **kwargs)
    return wrapper