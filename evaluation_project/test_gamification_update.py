import os
import sys
import django

# Configuration Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from analytics_dashboard.models import StudentProfile, Challenge, StudentTestResult
from analytics_dashboard.services import GamificationService
from django.utils import timezone

print("=== Test du système de gamification ===\n")

# Trouver l'étudiant
try:
    student = User.objects.get(username='etudiant2')
    print(f"✅ Étudiant: {student.username}\n")
except:
    print("❌ Utilisateur etudiant2 non trouvé")
    exit()

# Vérifier/créer le profil
profile, created = StudentProfile.objects.get_or_create(user=student)
if created:
    print("✅ Profil de gamification créé")
else:
    print(f"📊 Profil existant:")
    print(f"  - Niveau: {profile.level}")
    print(f"  - XP: {profile.total_xp}")
    print(f"  - Coins: {profile.coins}")
    print(f"  - Streak: {profile.current_streak}")
print()

# Vérifier les défis actifs
active_challenges = Challenge.objects.filter(student=student, status='ACTIVE')
print(f"🎯 Défis actifs: {active_challenges.count()}")
for challenge in active_challenges:
    print(f"\n  Défi: {challenge.title}")
    print(f"  - Sujet: {challenge.target_data.get('subject', 'N/A')}")
    print(f"  - Progression: {challenge.current_progress}%")
    print(f"  - Objectif: {challenge.target_data.get('exercises_count', 0)} exercices")
    print(f"  - Score requis: {challenge.target_data.get('min_score', 0)}%")
    print(f"  - Récompense: {challenge.xp_reward} XP + {challenge.coins_reward} coins")

print("\n\n=== Simulation d'un test complété ===")
print("On va créer un résultat de test pour la Biologie avec un score de 85%...\n")

# Créer un résultat de test simulé
test_result = StudentTestResult.objects.create(
    student=student,
    subject="Biologie",
    test_name="Test de Biologie Simulé",
    score=85,
    completed_at=timezone.now()
)
print(f"✅ Résultat de test créé: {test_result.test_name} - Score: {test_result.score}%")

# Mettre à jour manuellement les défis
gamification_service = GamificationService()

for challenge in active_challenges:
    challenge_subject = challenge.target_data.get('subject', '')
    
    if 'biologie' in challenge_subject.lower():
        print(f"\n🎯 Mise à jour du défi: {challenge.title}")
        
        # Compter les tests de biologie
        bio_tests = StudentTestResult.objects.filter(
            student=student,
            subject__icontains="Biologie"
        ).count()
        
        print(f"  Tests de Biologie complétés: {bio_tests}")
        
        # Mettre à jour le défi
        updated_challenge = gamification_service.update_challenge_progress(
            challenge=challenge,
            exercises_completed=bio_tests,
            current_score=85
        )
        
        print(f"  Nouvelle progression: {updated_challenge.current_progress}%")
        print(f"  Statut: {updated_challenge.status}")
        
        if updated_challenge.status == 'COMPLETED':
            print(f"  🎉 DÉFI TERMINÉ!")
            print(f"  Récompenses distribuées:")
            print(f"    - {challenge.xp_reward} XP")
            print(f"    - {challenge.coins_reward} coins")
            if challenge.badge_reward:
                print(f"    - Badge: {challenge.badge_reward}")

# Recharger le profil pour voir les changements
profile.refresh_from_db()
print(f"\n📊 Profil mis à jour:")
print(f"  - Niveau: {profile.level}")
print(f"  - XP: {profile.total_xp}")
print(f"  - Coins: {profile.coins}")
print(f"  - Défis complétés: {profile.challenges_completed}")
print(f"  - Badges: {len(profile.badges) if profile.badges else 0}")

print("\n✅ Test terminé! Rafraîchissez le dashboard pour voir les changements.")
