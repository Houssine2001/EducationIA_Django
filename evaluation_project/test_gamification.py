"""
Script de test pour vérifier que le système de gamification fonctionne correctement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile  # Utiliser UserProfile au lieu de StudentProfile
from analytics_dashboard.models import Challenge, StudentTestResult
from analytics_dashboard.services import ChallengeService
from datetime import datetime, timedelta
from django.utils import timezone

def test_gamification():
    print("="*80)
    print("🎮 TEST DU SYSTÈME DE GAMIFICATION")
    print("="*80)
    
    # 1. Trouver ou créer un étudiant
    try:
        student = User.objects.filter(is_staff=False).first()
        if not student:
            print("\n❌ Aucun étudiant trouvé dans la base de données")
            print("Veuillez créer un compte étudiant d'abord")
            return
        
        print(f"\n✅ Étudiant trouvé: {student.username} ({student.email})")
    except Exception as e:
        print(f"\n❌ Erreur lors de la récupération de l'étudiant: {e}")
        return
    
    # 2. Vérifier/créer le profil gamifié
    try:
        profile, created = UserProfile.objects.get_or_create(
            user=student,
            defaults={
                'role': 'student',
                'level': 1,
                'total_xp': 0
            }
        )
        if created:
            print(f"✅ Profil gamifié créé pour {student.username}")
        else:
            print(f"✅ Profil gamifié existe déjà")
        
        print(f"\n📊 Stats initiales:")
        print(f"   - Niveau: {profile.level}")
        print(f"   - XP Total: {profile.total_xp}")
        print(f"   - Badges: {len(profile.badges) if profile.badges else 0}")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du profil: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Générer des défis si nécessaire
    try:
        challenge_service = ChallengeService()
        active_challenges = Challenge.objects.filter(
            student=student,
            status='ACTIVE',
            expires_at__gte=timezone.now()
        )
        
        print(f"\n📝 Défis actifs: {active_challenges.count()}")
        
        if active_challenges.count() == 0:
            print("   🎯 Génération de nouveaux défis...")
            challenges = challenge_service.generate_daily_challenges(student)
            print(f"   ✅ {len(challenges)} défis générés !")
            
            for i, challenge in enumerate(challenges, 1):
                print(f"      {i}. {challenge.title} ({challenge.get_difficulty_display()})")
                print(f"         Récompense: {challenge.xp_reward} XP + {challenge.coins_reward} coins")
        else:
            print("   Défis existants:")
            for i, challenge in enumerate(active_challenges, 1):
                print(f"      {i}. {challenge.title}")
                print(f"         Progression: {challenge.current_progress}%")
                print(f"         Récompense: {challenge.xp_reward} XP + {challenge.coins_reward} coins")
    except Exception as e:
        print(f"\n❌ Erreur lors de la gestion des défis: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Simuler la complétion d'un test
    print(f"\n🧪 Simulation d'une complétion de test...")
    try:
        # Créer un StudentTestResult
        test_result = StudentTestResult.objects.create(
            student=student,
            subject="Mathématiques",
            test_name="Test de démonstration gamification",
            score=75.0
        )
        print(f"   ✅ Test créé: {test_result.test_name} - Score: {test_result.score}%")
        
        # Mettre à jour le profil
        challenge_service = ChallengeService()
        
        # Ajouter des XP automatiques
        base_xp = int(test_result.score / 10)
        if test_result.score >= 80:
            base_xp += 20
        elif test_result.score >= 60:
            base_xp += 10
        
        old_xp = profile.total_xp
        profile.total_xp += base_xp
        new_level = (profile.total_xp // 100) + 1
        level_up = new_level > profile.level
        profile.level = new_level
        profile.updated_at = timezone.now()
        profile.save()
        
        print(f"   💫 +{base_xp} XP ajoutés au profil (Total: {profile.total_xp})")
        if level_up:
            print(f"   🎊 LEVEL UP ! Nouveau niveau: {profile.level}")
        
        # Mettre à jour les défis
        active_challenges = Challenge.objects.filter(
            student=student,
            status='ACTIVE',
            expires_at__gte=timezone.now()
        )
        
        for challenge in active_challenges:
            if 'Mathématiques'.lower() in (challenge.subject or '').lower() or not challenge.subject:
                exercises_completed = StudentTestResult.objects.filter(
                    student=student,
                    completed_at__gte=challenge.created_at
                ).count()
                
                updated_challenge = challenge_service.update_challenge_progress(
                    challenge=challenge,
                    exercises_completed=exercises_completed,
                    current_score=test_result.score
                )
                
                print(f"   🎯 Défi mis à jour: {challenge.title}")
                print(f"      Progression: {updated_challenge.current_progress}%")
                
                if updated_challenge.status == 'COMPLETED':
                    print(f"      🎉 DÉFI COMPLÉTÉ !")
                    print(f"      Récompenses: {challenge.xp_reward} XP + {challenge.coins_reward} coins")
        
        # Recharger le profil pour afficher les stats finales
        profile.refresh_from_db()
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la simulation du test: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Afficher les stats finales
    print(f"\n📊 STATS FINALES:")
    print(f"   - Niveau: {profile.level}")
    print(f"   - XP Total: {profile.total_xp}")
    print(f"   - Badges: {len(profile.badges) if profile.badges else 0}")
    print(f"   - Tests complétés: {profile.total_tests_taken}")
    
    print(f"\n{'='*80}")
    print("✅ Test terminé avec succès !")
    print("\n💡 Conseils:")
    print("   1. Accédez au dashboard gamifié via: /analytics/gamified/")
    print("   2. Passez des tests pour gagner des XP et progresser")
    print("   3. Complétez des défis pour gagner des récompenses bonus")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    test_gamification()
