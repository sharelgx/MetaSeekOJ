#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ChoiceQuestion
from problem.models import Problem

print('=== Database Status Check ===')
print(f'ChoiceQuestion count: {ChoiceQuestion.objects.count()}')
print(f'Problem count: {Problem.objects.count()}')

print('\n=== Sample ChoiceQuestions ===')
for q in ChoiceQuestion.objects.all()[:3]:
    print(f'ID: {q.id}, Title: {q.title}')

print('\n=== Sample Problems ===')
for p in Problem.objects.all()[:3]:
    print(f'ID: {p.id}, Title: {p.title}')