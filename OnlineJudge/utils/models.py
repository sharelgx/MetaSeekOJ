# JSONField is not available in Django 2.1.7, using TextField as fallback
# from django.db.models import JSONField  # NOQA
try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    # Fallback for non-PostgreSQL databases or older Django versions
    from django.db import models
    JSONField = models.TextField
from django.db import models

from utils.xss_filter import XSSHtml


class RichTextField(models.TextField):
    def get_prep_value(self, value):
        with XSSHtml() as parser:
            return parser.clean(value or "")
