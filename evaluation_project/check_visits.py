import os
import sys
import django

# Configuration Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.subject_models import ChapterVisit, StudentSubjectProgress
from django.contrib.auth.models import User

print("=== Vérification des visites de chapitres ===\n")

# Trouver l'utilisateur étudiant
students = User.objects.filter(username__icontains='etudiant')
print(f"Étudiants trouvés: {students.count()}")
for student in students:
    print(f"  - {student.username} (ID: {student.id})")

print("\n=== Toutes les visites de chapitres ===")
all_visits = ChapterVisit.objects.all()
print(f"Nombre total de visites: {all_visits.count()}\n")

if all_visits.count() > 0:
    for visit in all_visits:
        print(f"Visite:")
        print(f"  - Étudiant: {visit.student.username}")
        print(f"  - Chapitre: {visit.chapter.title}")
        print(f"  - Terminé: {visit.completed}")
        print(f"  - Durée: {visit.duration_seconds}s")
        print(f"  - Date: {visit.visited_at}")
        print()
else:
    print("❌ AUCUNE VISITE ENREGISTRÉE dans ChapterVisit!")

print("\n=== Progressions des étudiants ===")
for progress in StudentSubjectProgress.objects.all():
    print(f"{progress.student.username} - {progress.subject.name}:")
    print(f"  - Visites: {progress.total_visits}")
    print(f"  - Chapitres visités: {progress.chapters_visited}")
    print(f"  - Chapitres terminés: {progress.chapters_completed}")
    print(f"  - Prédiction: {progress.predicted_success_rate}%")
    print()
