import os
import sys
import django

# Configuration Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.models import StudentProfile, PerformanceTrend
from django.contrib.auth.models import User

print("=== Vérification des données de gamification ===\n")

# Trouver etudiant2
try:
    student = User.objects.get(username='etudiant2')
    print(f"✅ Utilisateur trouvé: {student.username} (ID: {student.id})\n")
    
    # Vérifier le profil de gamification
    try:
        profile = StudentProfile.objects.get(user=student)
        print(f"📊 Profil de gamification:")
        print(f"  - Niveau: {profile.level}")
        print(f"  - XP: {profile.xp}")
        print(f"  - Coins: {profile.coins}")
        print(f"  - Streak: {profile.streak}")
        print(f"  - Tests réussis: {profile.tests_passed}")
        print(f"  - Tests échoués: {profile.tests_failed}")
        print(f"  - Prédiction IA: {profile.ai_prediction}%")
        print(f"  - Niveau de confiance: {profile.confidence_level}")
        print(f"  - Dernière activité: {profile.last_activity}\n")
    except StudentProfile.DoesNotExist:
        print("❌ Aucun profil de gamification trouvé!\n")
    
    # Vérifier les PerformanceTrend
    trends = PerformanceTrend.objects.filter(student=student)
    print(f"📈 PerformanceTrend trouvés: {trends.count()}")
    
    if trends.count() > 0:
        print("\nDétails des tendances:")
        for trend in trends:
            print(f"\n  Matière: {trend.subject}")
            print(f"  - Score: {trend.score}")
            print(f"  - Tests passés: {trend.tests_taken}")
            print(f"  - Tests réussis: {trend.tests_passed}")
            print(f"  - Moyenne: {trend.average_score}")
            print(f"  - Meilleur score: {trend.best_score}")
            print(f"  - Tendance: {trend.trend}")
            print(f"  - Niveau de confiance: {trend.confidence_level}")
            print(f"  - Date: {trend.date}")
    else:
        print("❌ Aucune tendance de performance trouvée!")
        
except User.DoesNotExist:
    print("❌ Utilisateur etudiant2 non trouvé!")

print("\n=== Fin de la vérification ===")
