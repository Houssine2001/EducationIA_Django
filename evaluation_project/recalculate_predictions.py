"""
Script pour recalculer toutes les prédictions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.subject_models import StudentSubjectProgress

print("Recalcul de toutes les prédictions...")

progresses = StudentSubjectProgress.objects.all()
print(f"Nombre de progressions trouvées: {progresses.count()}")

for progress in progresses:
    old_prediction = progress.predicted_success_rate
    progress.update_prediction()
    progress.save()
    print(f"  {progress.student.username} - {progress.subject.name}: {old_prediction}% → {progress.predicted_success_rate}%")

print("\n✅ Toutes les prédictions ont été recalculées!")
