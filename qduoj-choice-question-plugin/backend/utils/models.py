# Mock utils.models for testing
from django.db import models
from django.contrib.postgres.fields import JSONField as PostgresJSONField

# Mock JSONField
try:
    # Django 3.1+
    from django.db.models import JSONField
except ImportError:
    # Fallback for older Django versions
    JSONField = PostgresJSONField

# Mock RichTextField
class RichTextField(models.TextField):
    """Mock RichTextField for testing"""
    pass