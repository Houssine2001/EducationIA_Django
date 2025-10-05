import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Question

questions = Question.objects.filter(test_id=4).order_by('order')

for q in questions:
    print(f"\n{'='*60}")
    print(f"Question {q.order}: {q.question_text[:80]}")
    print(f"Type: {q.question_type}")
    print(f"Points: {q.points}")
    print(f"Options: {q.options}")
    print(f"Number of options: {len(q.options) if q.options else 0}")
