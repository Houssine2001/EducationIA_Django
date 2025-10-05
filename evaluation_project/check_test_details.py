"""
Script pour vérifier les détails du test React
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Test, Question

# Trouver le test React
react_test = Test.objects.filter(title__icontains='React').first()

if react_test:
    print(f"📝 Test: {react_test.title}")
    print(f"   Statut: {react_test.status}")
    print(f"   Durée: {react_test.duration} minutes")
    print(f"   Score de passage: {react_test.passing_score}%")
    print(f"   Points totaux: {react_test.total_points}")
    print(f"   Chronométré: {react_test.is_timed}")
    
    # Vérifier les questions
    questions = react_test.questions.all()
    print(f"\n📊 Questions ({questions.count()}):")
    
    total_points = 0
    for i, q in enumerate(questions, 1):
        print(f"\n   Question {i}:")
        print(f"   - Texte: {q.question_text[:50]}...")
        print(f"   - Type: {q.question_type}")
        print(f"   - Points: {q.points}")
        print(f"   - Ordre: {q.order}")
        total_points += q.points
    
    print(f"\n✅ Total des points des questions: {total_points}")
    print(f"   (devrait correspondre à total_points: {react_test.total_points})")
    
    # Mettre à jour si nécessaire
    if total_points != react_test.total_points:
        print(f"\n🔧 Mise à jour de total_points: {react_test.total_points} → {total_points}")
        react_test.total_points = total_points
        react_test.number_of_questions = questions.count()
        react_test.save()
        print("✅ Mis à jour!")
else:
    print("❌ Test React non trouvé")
