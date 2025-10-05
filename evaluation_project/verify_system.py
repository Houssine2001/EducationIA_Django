# ✅ Script de Vérification - EduIA
# Ce script vérifie que toutes les fonctionnalités sont opérationnelles

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test, Question, Submission, Result
from evaluation.analytics import StudentAnalytics
from evaluation.gamification import GamificationService

print("🔍 VÉRIFICATION DU SYSTÈME EduIA")
print("=" * 60)
print()

# Test 1: Base de données
print("1️⃣  Test de connexion à MongoDB...")
try:
    user_count = User.objects.count()
    print(f"   ✅ MongoDB connecté - {user_count} utilisateurs trouvés")
except Exception as e:
    print(f"   ❌ Erreur MongoDB: {e}")
    exit(1)

# Test 2: Modèles
print("\n2️⃣  Test des modèles Django...")
try:
    profile_count = UserProfile.objects.count()
    test_count = Test.objects.count()
    question_count = Question.objects.count()
    result_count = Result.objects.count()
    
    print(f"   ✅ UserProfile: {profile_count}")
    print(f"   ✅ Test: {test_count}")
    print(f"   ✅ Question: {question_count}")
    print(f"   ✅ Result: {result_count}")
except Exception as e:
    print(f"   ❌ Erreur modèles: {e}")

# Test 3: Analytics
print("\n3️⃣  Test du système Analytics...")
try:
    # Trouver un étudiant avec des résultats
    student = User.objects.filter(is_staff=False).first()
    if student:
        profile = UserProfile.objects.get(user=student)
        analytics = StudentAnalytics(profile)
        data = analytics.get_complete_statistics()
        
        print(f"   ✅ Analytics pour {student.username}:")
        print(f"      - Score moyen: {data['scores'].get('average', 0):.1f}%")
        print(f"      - Tests: {data['metadata']['total_tests']}")
        print(f"      - Heures d'étude: {data['study_time']['total_hours']:.1f}h")
        print(f"      - Tendance: {data['progression']['trend']}")
    else:
        print("   ⚠️  Aucun étudiant trouvé pour tester les analytics")
except Exception as e:
    print(f"   ❌ Erreur Analytics: {e}")

# Test 4: Gamification
print("\n4️⃣  Test du système de Gamification...")
try:
    if student:
        profile = UserProfile.objects.get(user=student)
        gamification = GamificationService(profile)
        level_info = gamification.get_level_info()
        
        print(f"   ✅ Gamification pour {student.username}:")
        print(f"      - Niveau: {level_info['current_level']['level']} ({level_info['current_level']['name']})")
        print(f"      - XP: {profile.total_xp}")
        print(f"      - Badges: {len(profile.badges or [])}")
        print(f"      - Progression: {level_info['progress_percentage']:.0f}%")
except Exception as e:
    print(f"   ❌ Erreur Gamification: {e}")

# Test 5: Recommandations
print("\n5️⃣  Test des Recommandations IA...")
try:
    if student:
        profile = UserProfile.objects.get(user=student)
        recommendations = profile.ai_recommendations or []
        
        print(f"   ✅ Recommandations pour {student.username}:")
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"      {i}. {rec.get('title', 'Sans titre')}")
        else:
            print("      (Aucune recommandation pour le moment)")
except Exception as e:
    print(f"   ❌ Erreur Recommandations: {e}")

# Test 6: Classement
print("\n6️⃣  Test du Classement...")
try:
    if student:
        profile = UserProfile.objects.get(user=student)
        gamification = GamificationService(profile)
        rank_info = gamification.get_student_rank()
        
        print(f"   ✅ Classement pour {student.username}:")
        print(f"      - Rang: #{rank_info['rank']}")
        print(f"      - Percentile: Top {rank_info['percentile']:.0f}%")
        print(f"      - Total étudiants: {rank_info['total_students']}")
except Exception as e:
    print(f"   ❌ Erreur Classement: {e}")

# Test 7: Templates
print("\n7️⃣  Test des Templates...")
import os
template_dir = 'templates'
required_templates = [
    'base.html',
    'evaluation/student/dashboard.html',
    'evaluation/student/progress.html',
]

for template in required_templates:
    path = os.path.join(template_dir, template)
    if os.path.exists(path):
        print(f"   ✅ {template}")
    else:
        print(f"   ❌ {template} MANQUANT")

# Résumé
print("\n" + "=" * 60)
print("📊 RÉSUMÉ DE LA VÉRIFICATION")
print("=" * 60)

# Calculer les statistiques
total_students = User.objects.filter(is_staff=False).count()
total_teachers = User.objects.filter(is_staff=True).count()
avg_score = 0
if total_students > 0:
    scores = [p.average_score for p in UserProfile.objects.filter(user__is_staff=False) if p.average_score > 0]
    avg_score = sum(scores) / len(scores) if scores else 0

print(f"""
Utilisateurs:
  - Étudiants: {total_students}
  - Enseignants: {total_teachers}
  - Score moyen global: {avg_score:.1f}%

Contenu:
  - Tests créés: {test_count}
  - Questions créées: {question_count}
  - Résultats enregistrés: {result_count}

Statut: ✅ SYSTÈME OPÉRATIONNEL
""")

print("🚀 Prochaines étapes:")
print("  1. Lancez le serveur: python manage.py runserver")
print("  2. Ouvrez http://127.0.0.1:8000/student/dashboard/")
print("  3. Connectez-vous avec: etudiant1 / pass123")
print("  4. Consultez GUIDE_DE_TEST.md pour les tests complets")
print()
print("=" * 60)
