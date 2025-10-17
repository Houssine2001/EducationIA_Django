import os
import sys
import django

# Configuration Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.subject_models import ChapterVisit, StudentSubjectProgress, Subject
from analytics_dashboard.subject_chapter_service import SubjectChapterService
from django.contrib.auth.models import User

print("=== Recalcul de toutes les progressions basées sur les visites ===\n")

# Pour chaque étudiant et chaque matière
all_progress = StudentSubjectProgress.objects.all()
print(f"Progressions trouvées: {all_progress.count()}\n")

service = SubjectChapterService()

for progress in all_progress:
    student = progress.student
    subject = progress.subject
    
    print(f"Traitement: {student.username} - {subject.code}")
    print(f"  Avant: visits={progress.total_visits}, visited={progress.chapters_visited}, completed={progress.chapters_completed}, prediction={progress.predicted_success_rate}%")
    
    # Récupérer toutes les visites pour cet étudiant et cette matière
    all_visits = list(ChapterVisit.objects.filter(
        student=student,
        chapter__subject=subject
    ))
    
    # Recalculer les métriques
    progress.total_visits = len(all_visits)
    progress.total_time_minutes = sum(v.duration_seconds for v in all_visits) // 60
    
    # Compter les chapitres uniques
    visited_chapter_ids = set(v.chapter._id for v in all_visits)
    progress.chapters_visited = len(visited_chapter_ids)
    
    # Compter les chapitres complétés
    completed_chapter_ids = set(v.chapter._id for v in all_visits if v.completed)
    progress.chapters_completed = len(completed_chapter_ids)
    
    # Calculer la consistance
    progress.consistency_score = service._calculate_consistency(student, subject)
    
    # Mettre à jour les scores de test
    service._update_test_scores(progress, student, subject)
    
    # Recalculer la prédiction
    progress.update_prediction()
    progress.save()
    
    print(f"  Après: visits={progress.total_visits}, visited={progress.chapters_visited}, completed={progress.chapters_completed}, prediction={progress.predicted_success_rate}%")
    print()

print("✅ Toutes les progressions ont été recalculées!")
