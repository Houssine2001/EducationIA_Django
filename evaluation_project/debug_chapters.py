"""
Script de diagnostic pour vérifier les chapitres
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.subject_models import Subject, Chapter
from analytics_dashboard.subject_chapter_service import SubjectChapterService
from django.contrib.auth.models import User

print("=" * 80)
print("DIAGNOSTIC DES CHAPITRES")
print("=" * 80)

# 1. Vérifier les matières
print("\n1. MATIÈRES DANS LA BASE:")
subjects = Subject.objects.all()
print(f"   Nombre total: {subjects.count()}")
for s in subjects:
    print(f"   - {s.name} (ID: {s._id})")

# 2. Vérifier les chapitres
print("\n2. CHAPITRES DANS LA BASE:")
chapters = Chapter.objects.all()
print(f"   Nombre total: {chapters.count()}")

# 3. Vérifier les chapitres par matière
print("\n3. CHAPITRES PAR MATIÈRE:")
for subject in subjects:
    chapters_list = Chapter.objects.filter(subject=subject).order_by('order')
    print(f"\n   {subject.name}: {chapters_list.count()} chapitres")
    for ch in chapters_list:
        print(f"      [{ch.order}] {ch.title} ({ch.difficulty}) - {ch.duration_minutes}min")

# 4. Tester le service
print("\n4. TEST DU SERVICE:")
service = SubjectChapterService()
math_subject = Subject.objects.filter(name__icontains='Math').first()
if math_subject:
    print(f"   Test avec: {math_subject.name} (ID: {math_subject._id})")
    subject, chapters = service.get_subject_with_chapters(str(math_subject._id))
    print(f"   Résultat service: {len(chapters)} chapitres")
    if chapters:
        print("   Premiers chapitres:")
        for ch in chapters[:3]:
            print(f"      - {ch.title}")
else:
    print("   ❌ Aucune matière 'Mathématiques' trouvée")

# 5. Tester avec un étudiant
print("\n5. TEST AVEC UN ÉTUDIANT:")
student = User.objects.filter(username='etudiant2').first()
if student and math_subject:
    print(f"   Étudiant: {student.username}")
    chapter_status = service.get_student_chapter_status(student, math_subject)
    print(f"   Statuts générés: {len(chapter_status)}")
    for item in chapter_status[:3]:
        print(f"      - {item['chapter'].title}: visité={item['is_visited']}, complété={item['is_completed']}")
else:
    print("   ❌ Étudiant 'etudiant2' non trouvé")

# 6. Vérifier la structure de données pour le template
print("\n6. STRUCTURE POUR LE TEMPLATE:")
if student and math_subject:
    chapters_with_status = []
    for item in chapter_status:
        chapters_with_status.append({
            'chapter': item['chapter'],
            'status': {
                'visited': item['is_visited'],
                'completed': item['is_completed'],
                'visit_count': item['visit_count'],
                'total_time_minutes': item['total_time_minutes'],
                'progress_percentage': item['progress_percentage']
            }
        })
    print(f"   Chapitres formatés: {len(chapters_with_status)}")
    if chapters_with_status:
        print("   Premier élément:")
        first = chapters_with_status[0]
        print(f"      chapter.title: {first['chapter'].title}")
        print(f"      chapter.pk: {first['chapter'].pk}")
        print(f"      status.visited: {first['status']['visited']}")
        print(f"      status.completed: {first['status']['completed']}")

print("\n" + "=" * 80)
print("DIAGNOSTIC TERMINÉ")
print("=" * 80)
