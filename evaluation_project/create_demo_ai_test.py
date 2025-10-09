"""
Script pour créer un test IA de démonstration.
Permet de tester visuellement l'intégration des tests IA dans l'interface étudiant.
"""

import os
import django
import sys

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation_project.settings')
django.setup()

from evaluation.models import Test, Question
from django.contrib.auth import get_user_model

User = get_user_model()


def create_demo_ai_test():
    """
    Crée un test IA de démonstration pour tester l'intégration.
    """
    print("🤖 Création d'un test IA de démonstration...")
    
    # Récupérer un professeur (premier utilisateur staff)
    teacher = User.objects.filter(is_staff=True).first()
    
    if not teacher:
        print("❌ Aucun professeur trouvé. Créez d'abord un compte professeur.")
        return
    
    print(f"✅ Professeur: {teacher.username}")
    
    # Créer le test IA
    test = Test.objects.create(
        title="Test IA - Mathématiques Niveau 2",
        description="Test généré automatiquement par l'IA sur les équations du second degré. "
                   "Ce test adapte sa difficulté en fonction de vos performances précédentes.",
        subject="Mathématiques",
        topic="Équations du Second Degré",
        source_type='ai_generated',  # 🔑 TYPE IA
        created_by=teacher,
        difficulty='medium',
        duration=30,
        passing_score=60.0,
        total_points=100.0,
        status='published',  # Publié pour que les étudiants le voient
        is_timed=True,
        allow_review=True,
        shuffle_questions=True,
        tags=['algèbre', 'équations', 'niveau-2', 'ia-généré'],
        skills_tested=['Résolution équations', 'Calcul discriminant', 'Factorisation'],
        ai_metadata={
            'generated_at': '2025-10-09',
            'model': 'gpt-4',
            'difficulty_level': 'adaptive',
            'student_level_target': 'intermediate'
        }
    )
    
    print(f"✅ Test créé: {test.title} (ID: {test.id})")
    print(f"   Type: {test.get_source_type_display()}")
    print(f"   IA? {test.is_ai_generated()}")
    
    # Créer des questions de démonstration
    questions_data = [
        {
            'question_text': "Résoudre l'équation: x² - 5x + 6 = 0",
            'question_type': 'mcq',
            'points': 10,
            'options': [
                {'text': 'x = 2 ou x = 3', 'is_correct': True},
                {'text': 'x = 1 ou x = 6', 'is_correct': False},
                {'text': 'x = -2 ou x = -3', 'is_correct': False},
                {'text': 'Aucune solution', 'is_correct': False},
            ],
            'explanation': "Le discriminant Δ = 25 - 24 = 1 > 0, donc deux solutions réelles: x₁ = (5+1)/2 = 3 et x₂ = (5-1)/2 = 2"
        },
        {
            'question_text': "Quel est le discriminant de l'équation 2x² + 3x - 2 = 0 ?",
            'question_type': 'mcq',
            'points': 10,
            'options': [
                {'text': 'Δ = 25', 'is_correct': True},
                {'text': 'Δ = 9', 'is_correct': False},
                {'text': 'Δ = 16', 'is_correct': False},
                {'text': 'Δ = -7', 'is_correct': False},
            ],
            'explanation': "Δ = b² - 4ac = 3² - 4(2)(-2) = 9 + 16 = 25"
        },
        {
            'question_text': "L'équation x² + 4x + 4 = 0 a combien de solutions ?",
            'question_type': 'mcq',
            'points': 10,
            'options': [
                {'text': 'Une solution double (x = -2)', 'is_correct': True},
                {'text': 'Deux solutions distinctes', 'is_correct': False},
                {'text': 'Aucune solution réelle', 'is_correct': False},
                {'text': 'Infinité de solutions', 'is_correct': False},
            ],
            'explanation': "Δ = 16 - 16 = 0, donc une solution double: x = -4/2 = -2"
        },
        {
            'question_text': "Factoriser: x² - 9",
            'question_type': 'short_answer',
            'points': 10,
            'correct_answer': '(x-3)(x+3)',
            'explanation': "C'est une différence de carrés: a² - b² = (a-b)(a+b)"
        },
        {
            'question_text': "L'équation x² + x + 1 = 0 a-t-elle des solutions réelles ?",
            'question_type': 'true_false',
            'points': 10,
            'correct_answer': False,
            'explanation': "Δ = 1 - 4 = -3 < 0, donc aucune solution réelle"
        },
    ]
    
    question_order = 1
    for q_data in questions_data:
        question = Question.objects.create(
            test=test,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            points=q_data['points'],
            order=question_order,
            explanation=q_data.get('explanation', ''),
            correct_answer=q_data.get('correct_answer'),
        )
        
        # Ajouter les options si MCQ
        if q_data['question_type'] == 'mcq':
            question.options = q_data['options']
            question.save()
        
        print(f"   ✅ Question {question_order}: {q_data['question_text'][:50]}...")
        question_order += 1
    
    # Mettre à jour le nombre de questions
    test.number_of_questions = question_order - 1
    test.save()
    
    print(f"\n✅ Test IA créé avec succès!")
    print(f"   📊 {test.number_of_questions} questions")
    print(f"   🎯 Difficulté: {test.get_difficulty_display()}")
    print(f"   ⏱️  Durée: {test.duration} minutes")
    print(f"   📈 Score minimum: {test.passing_score}%")
    print(f"\n🚀 Le test est maintenant visible pour tous les étudiants!")
    print(f"   Badge 🤖 IA sera affiché automatiquement")
    
    return test


def create_manual_test_for_comparison():
    """
    Crée un test manuel pour comparaison.
    """
    print("\n👔 Création d'un test manuel pour comparaison...")
    
    teacher = User.objects.filter(is_staff=True).first()
    
    if not teacher:
        print("❌ Aucun professeur trouvé.")
        return
    
    test = Test.objects.create(
        title="Test Manuel - Mathématiques Niveau 2",
        description="Test créé manuellement par le professeur sur les équations.",
        subject="Mathématiques",
        topic="Équations du Second Degré",
        source_type='manual',  # 🔑 TYPE MANUEL
        created_by=teacher,
        difficulty='medium',
        duration=30,
        passing_score=60.0,
        total_points=50.0,
        status='published',
        is_timed=True,
        number_of_questions=5
    )
    
    print(f"✅ Test manuel créé: {test.title} (ID: {test.id})")
    print(f"   Type: {test.get_source_type_display()}")
    print(f"   Badge 👔 Manuel sera affiché")
    
    return test


def verify_integration():
    """
    Vérifie que l'intégration fonctionne.
    """
    print("\n🔍 Vérification de l'intégration...\n")
    
    # Compter les tests
    all_tests = Test.objects.filter(status='published')
    ai_tests = Test.objects.filter(status='published', source_type='ai_generated')
    manual_tests = Test.objects.filter(status='published', source_type='manual')
    
    print(f"📊 Tests publiés:")
    print(f"   Total: {all_tests.count()}")
    print(f"   🤖 IA: {ai_tests.count()}")
    print(f"   👔 Manuels: {manual_tests.count()}")
    
    if ai_tests.count() > 0:
        print(f"\n✅ Tests IA détectés:")
        for test in ai_tests[:3]:
            print(f"   • {test.title}")
            print(f"     is_ai_generated() = {test.is_ai_generated()}")
            print(f"     Badge HTML: {test.get_source_badge()}")
    
    print(f"\n📝 Pour tester l'interface:")
    print(f"   1. Connectez-vous comme étudiant")
    print(f"   2. Allez sur le dashboard")
    print(f"   3. Vérifiez le badge 🤖 IA sur les tests")
    print(f"   4. Allez dans 'Mes Tests'")
    print(f"   5. Testez les filtres 'Tests IA' et 'Tests Manuels'")


if __name__ == "__main__":
    print("="*60)
    print("🤖 CRÉATION DE TESTS IA DE DÉMONSTRATION")
    print("="*60 + "\n")
    
    # Créer un test IA
    ai_test = create_demo_ai_test()
    
    # Créer un test manuel pour comparaison
    manual_test = create_manual_test_for_comparison()
    
    # Vérifier l'intégration
    verify_integration()
    
    print("\n" + "="*60)
    print("✅ TERMINÉ!")
    print("="*60)
