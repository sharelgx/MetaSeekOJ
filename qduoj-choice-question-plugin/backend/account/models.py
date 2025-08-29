# Mock account.models for testing
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Mock User model for testing"""
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='account_user_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='account_user_set'
    )
    
    class Meta:
        db_table = 'user'