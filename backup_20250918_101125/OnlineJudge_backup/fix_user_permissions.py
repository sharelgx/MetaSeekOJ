#!/usr/bin/env python3
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from account.models import User, ProblemPermission, AdminType

try:
    # Get root user
    user = User.objects.get(username='root')
    
    print("Current permissions:")
    print(f"  admin_type: {user.admin_type}")
    print(f"  problem_permission: {user.problem_permission}")
    
    # Update permissions with correct values
    user.admin_type = AdminType.SUPER_ADMIN
    user.problem_permission = ProblemPermission.ALL
    user.save()
    
    print("\nPermissions updated successfully!")
    print(f"  New admin_type: {user.admin_type}")
    print(f"  New problem_permission: {user.problem_permission}")
    
    # Verify the constants
    print("\nConstants verification:")
    print(f"  AdminType.SUPER_ADMIN = '{AdminType.SUPER_ADMIN}'")
    print(f"  ProblemPermission.ALL = '{ProblemPermission.ALL}'")
    
except User.DoesNotExist:
    print("Error: Root user not found!")
except Exception as e:
    print(f"Error: {e}")