# 🤖 Script de Test Automatique - EduIA

## Ce script crée automatiquement des données de test

import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test, Question, Submission, Result

print("🚀 Démarrage du script de test automatique...\n")

# ===================================================================
# 1. CRÉER LES UTILISATEURS
# ===================================================================
print("📝 Étape 1/6 : Création des utilisateurs...")

# Supprimer les utilisateurs de test existants
User.objects.filter(username__startswith='test_').delete()
User.objects.filter(username__in=['etudiant1', 'etudiant2', 'etudiant3', 'prof1']).delete()

# Créer 3 étudiants
etudiants = []
for i in range(1, 4):
    user = User.objects.create_user(
        username=f'etudiant{i}',
        email=f'etudiant{i}@eduia.com',
        password='pass123',
        first_name=f'Étudiant',
        last_name=f'Test{i}'
    )
    etudiants.append(user)
    print(f"  ✅ Créé: {user.username} (mot de passe: pass123)")

# Créer 1 enseignant
prof = User.objects.create_user(
    username='prof1',
    email='prof@eduia.com',
    password='pass123',
    first_name='Professeur',
    last_name='Test',
    is_staff=True
)
print(f"  ✅ Créé: {prof.username} (mot de passe: pass123, Staff: True)\n")

# ===================================================================
# 2. VÉRIFIER LES PROFILS
# ===================================================================
print("👤 Étape 2/6 : Vérification des profils utilisateurs...")

for user in [*etudiants, prof]:
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        print(f"  ✅ Profil créé pour {user.username}")
    else:
        print(f"  ℹ️  Profil existant pour {user.username}")

print()

# ===================================================================
# 3. CRÉER LES TESTS
# ===================================================================
print("📚 Étape 3/6 : Création des tests...")

# Supprimer les anciens tests de test
Test.objects.filter(created_by=prof).delete()

tests_data = [
    {
        'title': 'Algèbre Niveau 1',
        'subject': 'Mathématiques',
        'description': 'Test de base en algèbre pour débutants',
        'difficulty': 'beginner',
        'time_limit': 30,
        'questions': [
            {'text': '2 + 2 = ?', 'type': 'mcq', 'choices': ['3', '4', '5', '6'], 'correct': '4', 'points': 2},
            {'text': '5 × 3 = ?', 'type': 'mcq', 'choices': ['10', '15', '20', '25'], 'correct': '15', 'points': 2},
            {'text': 'Résolvez : x + 5 = 10', 'type': 'text', 'correct': 'x = 5', 'points': 3},
            {'text': 'Racine carrée de 16 ?', 'type': 'mcq', 'choices': ['2', '4', '8', '16'], 'correct': '4', 'points': 2},
            {'text': '10 - 7 = ?', 'type': 'mcq', 'choices': ['1', '2', '3', '4'], 'correct': '3', 'points': 1},
        ]
    },
    {
        'title': 'Forces et Mouvement',
        'subject': 'Physique',
        'description': 'Comprendre les concepts de base de la mécanique',
        'difficulty': 'intermediate',
        'time_limit': 45,
        'questions': [
            {'text': 'F = m × a représente ?', 'type': 'mcq', 'choices': ['Loi de Newton', 'Loi de Coulomb', 'Loi d\'Ohm', 'Loi de Kepler'], 'correct': 'Loi de Newton', 'points': 2},
            {'text': 'Calculez la force si m=5kg et a=2m/s²', 'type': 'text', 'correct': 'F = 10N', 'points': 3},
            {'text': 'Unité de la force ?', 'type': 'mcq', 'choices': ['Joule', 'Newton', 'Watt', 'Pascal'], 'correct': 'Newton', 'points': 2},
            {'text': 'Vitesse = ?', 'type': 'mcq', 'choices': ['Distance / Temps', 'Temps / Distance', 'Force / Masse', 'Masse / Force'], 'correct': 'Distance / Temps', 'points': 2},
            {'text': 'Qu\'est-ce que l\'accélération ?', 'type': 'text', 'correct': 'variation de vitesse', 'points': 1},
        ]
    },
    {
        'title': 'Introduction Python',
        'subject': 'Informatique',
        'description': 'Concepts de base de Python',
        'difficulty': 'beginner',
        'time_limit': 20,
        'questions': [
            {'text': 'Python est ?', 'type': 'mcq', 'choices': ['Langage de programmation', 'Base de données', 'Système d\'exploitation', 'Framework'], 'correct': 'Langage de programmation', 'points': 1},
            {'text': 'print() est ?', 'type': 'mcq', 'choices': ['Fonction d\'affichage', 'Variable', 'Classe', 'Module'], 'correct': 'Fonction d\'affichage', 'points': 1},
            {'text': 'Écrivez un code pour afficher "Hello"', 'type': 'text', 'correct': 'print("Hello")', 'points': 3},
            {'text': 'Type de 3.14 ?', 'type': 'mcq', 'choices': ['int', 'float', 'str', 'bool'], 'correct': 'float', 'points': 2},
            {'text': 'Opérateur de comparaison ?', 'type': 'mcq', 'choices': ['=', '==', '===', ':='], 'correct': '==', 'points': 3},
        ]
    }
]

created_tests = []

for test_data in tests_data:
    # Créer le test
    test = Test.objects.create(
        title=test_data['title'],
        subject=test_data['subject'],
        description=test_data['description'],
        difficulty=test_data['difficulty'],
        duration=test_data['time_limit'],  # time_limit → duration
        created_by=prof,
        status='published'  # Publié au lieu de draft
    )
    
    # Créer les questions
    for idx, q_data in enumerate(test_data['questions'], 1):
        # Préparer les options pour QCM
        options = []
        if 'choices' in q_data:
            for choice in q_data['choices']:
                options.append({
                    'text': choice,
                    'is_correct': choice == q_data['correct']
                })
        
        Question.objects.create(
            test=test,
            question_text=q_data['text'],  # text → question_text
            question_type=q_data['type'],  # type → question_type
            options=options,  # choices → options avec structure correcte
            correct_answer=q_data['correct'],
            points=q_data['points'],
            order=idx
        )
    
    created_tests.append(test)
    print(f"  ✅ Créé: {test.title} ({test.questions.count()} questions)")

print()

# ===================================================================
# 4. SIMULER LES PASSAGES DE TESTS
# ===================================================================
print("🎯 Étape 4/6 : Simulation des passages de tests...")

# Scénarios de réponses pour chaque étudiant
scenarios = {
    'etudiant1': {
        'Algèbre Niveau 1': {'correct': 4, 'total': 5, 'time': 15},  # 80%
        'Forces et Mouvement': {'correct': 3, 'total': 5, 'time': 25},  # 60%
        'Introduction Python': {'correct': 5, 'total': 5, 'time': 10},  # 100%
    },
    'etudiant2': {
        'Algèbre Niveau 1': {'correct': 3, 'total': 5, 'time': 20},  # 60%
        'Forces et Mouvement': {'correct': 2, 'total': 5, 'time': 30},  # 40%
        'Introduction Python': {'correct': 4, 'total': 5, 'time': 15},  # 80%
    },
    'etudiant3': {
        'Algèbre Niveau 1': {'correct': 5, 'total': 5, 'time': 12},  # 100%
        'Forces et Mouvement': {'correct': 4, 'total': 5, 'time': 20},  # 80%
        'Introduction Python': {'correct': 5, 'total': 5, 'time': 8},  # 100%
    }
}

for student in etudiants:
    student_scenarios = scenarios[student.username]
    
    for test in created_tests:
        if test.title in student_scenarios:
            scenario = student_scenarios[test.title]
            
            # Créer la soumission
            submission = Submission.objects.create(
                test=test,
                student=student,
                started_at=timezone.now() - timedelta(minutes=scenario['time']),
                submitted_at=timezone.now(),
                time_spent=scenario['time']
            )
            
            # Créer les réponses
            questions = list(test.questions.all())
            answers = {}
            for i, question in enumerate(questions):
                # Répondre correctement ou non selon le scénario
                if i < scenario['correct']:
                    answers[str(question.id)] = question.correct_answer
                else:
                    # Mauvaise réponse
                    if question.question_type == 'mcq' and question.options:  # choices → options
                        # Extraire les textes des options
                        all_options = [opt['text'] for opt in question.options]
                        wrong = [opt for opt in all_options if opt != question.correct_answer]
                        answers[str(question.id)] = wrong[0] if wrong else ''
                    else:
                        answers[str(question.id)] = 'mauvaise réponse'
            
            submission.answers = answers
            submission.save()
            
            # Calculer le score
            total_points = sum([q.points for q in questions])
            earned_points = sum([q.points for i, q in enumerate(questions) if i < scenario['correct']])
            percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
            
            # Créer le résultat
            Result.objects.create(
                submission=submission,
                test=test,
                student=student,
                total_score=earned_points,  # score → total_score
                percentage_score=percentage,  # percentage → percentage_score
                ai_analysis={
                    'strengths': ['Bon score global'] if percentage >= 70 else [],
                    'weaknesses': ['Besoin de révisions'] if percentage < 70 else [],
                    'recommendations': []
                }
            )
            
            print(f"  ✅ {student.username} a passé '{test.title}': {percentage:.1f}% en {scenario['time']} min")

print()

# ===================================================================
# 5. METTRE À JOUR LES PROFILS AVEC ANALYTICS
# ===================================================================
print("📊 Étape 5/6 : Mise à jour des profils avec analytics...")

from evaluation.analytics import StudentAnalytics, update_student_profile_with_recommendations
from evaluation.gamification import GamificationService

for student in etudiants:
    profile = UserProfile.objects.get(user=student)
    
    # Mettre à jour les statistiques de base
    results = list(Result.objects.filter(student=student))
    if len(results) > 0:
        profile.total_tests_taken = len(results)
        profile.average_score = sum(r.total_score for r in results) / len(results)
        profile.save()
    
    print(f"  ✅ Profil mis à jour pour {student.username}: {len(results)} tests, moyenne {profile.average_score:.1f}%")

print()

# ===================================================================
# 6. RÉSUMÉ
# ===================================================================
print("=" * 60)
print("✅ SCRIPT DE TEST TERMINÉ AVEC SUCCÈS !")
print("=" * 60)
print()
print("📊 Résumé:")
print(f"  - Utilisateurs créés: {User.objects.count() - 1} (+ 1 admin)")
print(f"  - Tests créés: {Test.objects.count()}")
print(f"  - Questions créées: {Question.objects.count()}")
print(f"  - Soumissions: {Submission.objects.count()}")
print(f"  - Résultats: {Result.objects.count()}")
print()
print("🔑 Comptes de test créés:")
print("  - etudiant1 / pass123 (Score moyen: 80%)")
print("  - etudiant2 / pass123 (Score moyen: 60%)")
print("  - etudiant3 / pass123 (Score moyen: 93%)")
print("  - prof1 / pass123 (Enseignant)")
print()
print("🌐 Étapes suivantes:")
print("  1. Démarrez le serveur: python manage.py runserver")
print("  2. Connectez-vous avec un compte étudiant")
print("  3. Consultez le tableau de bord et la progression")
print("  4. Vérifiez les graphiques et les analytics")
print()
print("📖 Consultez GUIDE_DE_TEST.md pour les tests manuels détaillés")
print("=" * 60)
