"""
Script de migration des badges - Convertir l'ancien format au nouveau format
"""

import os
import django
import sys

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import UserProfile
from evaluation.gamification import GamificationService

def migrate_badges():
    """Migrer les badges de l'ancien format au nouveau format"""
    
    print("=" * 80)
    print("MIGRATION DES BADGES")
    print("=" * 80)
    
    profiles = UserProfile.objects.all()
    
    for profile in profiles:
        print(f"\n🔄 Migration pour {profile.user.username}...")
        
        # Récupérer les badges actuels
        current_badges = profile.badges
        should_check_badges = False
        
        if not current_badges:
            print("  ✅ Aucun badge existant")
            # Initialiser avec une liste vide
            profile.badges = []
            profile.save()
            should_check_badges = True
        elif isinstance(current_badges, list) and len(current_badges) > 0:
            first_badge = current_badges[0]
            
            # Si c'est le nouveau format (a badge_id), pas besoin de migration
            if isinstance(first_badge, dict) and 'badge_id' in first_badge:
                print(f"  ✅ Badges déjà au nouveau format ({len(current_badges)} badges)")
                continue
            
            # Ancien format - nettoyer et réinitialiser
            print(f"  🔄 Ancien format détecté ({len(current_badges)} badges)")
            print("  ❌ Réinitialisation du système de badges...")
            
            # Réinitialiser les badges
            profile.badges = []
            profile.total_xp = 0
            profile.level = 1
            profile.save()
            
            print("  ✅ Profil réinitialisé")
            should_check_badges = True
        
        # Forcer la vérification des badges avec le nouveau système
        if should_check_badges:
            print("  🔍 Vérification des nouveaux badges...")
            try:
                gamification_service = GamificationService(profile)
                new_badges = gamification_service.check_and_award_badges()
                
                if new_badges:
                    print(f"  🎉 {len(new_badges)} nouveaux badges attribués:")
                    for badge in new_badges:
                        print(f"    - {badge['icon']} {badge['name']} (+{badge['points']} XP)")
                else:
                    print("  ℹ️ Aucun badge attribué pour le moment")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("MIGRATION TERMINÉE")
    print("=" * 80)

if __name__ == '__main__':
    migrate_badges()
