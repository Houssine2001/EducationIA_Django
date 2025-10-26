"""
Script de test pour le système de badges
Affiche les données de l'utilisateur et force la vérification des badges
"""

import os
import django
import sys

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile, Result, Submission
from evaluation.gamification import GamificationService

def test_badge_system():
    """Tester le système de badges pour l'étudiant"""
    
    print("=" * 80)
    print("TEST DU SYSTÈME DE BADGES")
    print("=" * 80)
    
    # Récupérer l'étudiant (username: etudiant1)
    try:
        user = User.objects.get(username='etudiant1')
        print(f"\n✅ Utilisateur trouvé: {user.username} ({user.get_full_name()})")
    except User.DoesNotExist:
        print("❌ Utilisateur 'etudiant1' non trouvé")
        return
    
    # Récupérer ou créer le profil
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if created:
        print("✅ Profil créé")
    else:
        print("✅ Profil existant trouvé")
    
    print(f"\nProfil actuel:")
    print(f"  - Niveau: {profile.level}")
    print(f"  - XP Total: {profile.total_xp}")
    print(f"  - Badges actuels: {profile.badges}")
    print(f"  - Current Streak: {profile.current_streak}")
    
    # Récupérer les résultats
    results = Result.objects.filter(student=user)
    submissions = Submission.objects.filter(student=user, status='completed')
    
    print(f"\nStatistiques de l'étudiant:")
    print(f"  - Nombre de tests manuels: {results.count()}")
    print(f"  - Nombre de tests IA: {submissions.count()}")
    
    if results.count() > 0:
        perfect_scores = results.filter(percentage_score=100).count()
        high_scores = results.filter(percentage_score__gte=90).count()
        print(f"  - Tests avec 100%: {perfect_scores}")
        print(f"  - Tests avec ≥90%: {high_scores}")
        
        # Afficher quelques résultats
        print(f"\n  Derniers tests:")
        for r in results.order_by('-created_at')[:5]:
            print(f"    - {r.test.title}: {r.percentage_score}%")
    
    # Créer le service de gamification
    print("\n" + "=" * 80)
    print("VÉRIFICATION DES BADGES")
    print("=" * 80)
    
    gamification_service = GamificationService(profile)
    
    # Forcer la vérification des badges
    print("\n🔍 Vérification et attribution des badges...")
    try:
        new_badges = gamification_service.check_and_award_badges()
        
        if new_badges:
            print(f"\n🎉 {len(new_badges)} NOUVEAUX BADGES OBTENUS:")
            for badge in new_badges:
                print(f"  ✨ {badge['icon']} {badge['name']}")
                print(f"     {badge['description']}")
                print(f"     +{badge['points']} XP")
        else:
            print("\n✅ Aucun nouveau badge (déjà tous obtenus ou conditions non remplies)")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification des badges: {e}")
        import traceback
        traceback.print_exc()
    
    # Recharger le profil pour voir les changements
    profile.refresh_from_db()
    
    print(f"\nProfil après vérification:")
    print(f"  - Niveau: {profile.level}")
    print(f"  - XP Total: {profile.total_xp}")
    print(f"  - Nombre de badges: {len(profile.badges or [])}")
    
    # Obtenir la progression de tous les badges
    print("\n" + "=" * 80)
    print("PROGRESSION DES BADGES")
    print("=" * 80)
    
    try:
        badge_progress = gamification_service.get_badge_progress()
        
        earned = badge_progress['earned_badges']
        available = badge_progress['available_badges']
        
        print(f"\n✅ Badges obtenus: {len(earned)}")
        if earned:
            for b in earned:
                print(f"  🏆 {b['icon']} {b['name']} - {b['points']} XP")
        
        print(f"\n📊 Badges disponibles: {len(available)}")
        if available:
            # Trier par progression décroissante
            available_sorted = sorted(available, key=lambda x: x['progress_percentage'], reverse=True)
            
            for b in available_sorted[:10]:  # Top 10
                progress_bar = "█" * int(b['progress_percentage'] / 10) + "░" * (10 - int(b['progress_percentage'] / 10))
                print(f"  {b['icon']} {b['name']}")
                print(f"     [{progress_bar}] {b['progress_percentage']:.1f}% ({b['progress']}/{b['target']})")
                print(f"     {b['description']}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de get_badge_progress: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("FIN DU TEST")
    print("=" * 80)

if __name__ == '__main__':
    test_badge_system()
