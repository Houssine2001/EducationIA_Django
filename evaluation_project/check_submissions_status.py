import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Submission, Result
from django.db.models import Count

print("Total Submissions:", Submission.objects.all().count())
print("Total Results:", Result.objects.all().count())
print("\nStatuts des soumissions:")
for s in Submission.objects.values('status').annotate(count=Count('id')):
    print(f"  {s['status']}: {s['count']}")

print("\nDernières soumissions:")
for sub in Submission.objects.all().order_by('-id')[:5]:
    print(f"  #{sub.id} - {sub.student.username} - {sub.test.title} - Status: {sub.status}")
    try:
        result = Result.objects.get(submission=sub)
        print(f"    Score: {result.total_score} ({result.percentage_score:.1f}%)")
    except Result.DoesNotExist:
        print(f"    Pas de résultat")
