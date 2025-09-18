# Use Django 4.2 compatible JSONField
from django.db.models import JSONField
from django.db import models

from utils.xss_filter import XSSHtml


class RichTextField(models.TextField):
    def get_prep_value(self, value):
        with XSSHtml() as parser:
            return parser.clean(value or "")
