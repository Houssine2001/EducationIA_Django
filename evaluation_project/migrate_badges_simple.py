#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migration des badges vers le nouveau format (sans emojis pour Windows).
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation_project.settings')
django.setup()

from evaluation.models import UserProfile
from evaluation.gamification import GamificationService


def migrate_badges():
    """Migrer tous les badges vers le nouveau format."""
    print("=" * 80)
    print("MIGRATION DES BADGES")
    print("=" * 80)
    
    profiles = UserProfile.objects.all()
    
    for profile in profiles:
        print(f"\n> Migration pour {profile.user.username}...")
        
        # Récupérer les badges actuels
        current_badges = profile.badges
        should_check_badges = False
        
        if not current_badges:
            print("  [OK] Aucun badge existant - initialisation...")
            profile.badges = []
            profile.save()
            should_check_badges = True
        elif isinstance(current_badges, list) and len(current_badges) > 0:
            first_badge = current_badges[0]
            
            # Si c'est le nouveau format (a badge_id), pas besoin de migration
            if isinstance(first_badge, dict) and 'badge_id' in first_badge:
                print(f"  [OK] Badges deja au nouveau format ({len(current_badges)} badges)")
                continue
            
            # Ancien format - nettoyer et réinitialiser
            print(f"  [WARN] Ancien format detecte ({len(current_badges)} badges)")
            print("  [INFO] Reinitialisation du systeme...")
            
            # Réinitialiser les badges
            profile.badges = []
            profile.total_xp = 0
            profile.level = 1
            profile.save()
            
            print("  [OK] Profil reinitialise")
            should_check_badges = True
        
        # Forcer la vérification des badges avec le nouveau système
        if should_check_badges:
            print("  [INFO] Verification des nouveaux badges...")
            try:
                gamification_service = GamificationService(profile)
                new_badges = gamification_service.check_and_award_badges()
                
                if new_badges:
                    print(f"  [SUCCESS] {len(new_badges)} nouveaux badges attribues:")
                    for badge in new_badges:
                        # Pas d'icone emoji pour éviter les problèmes d'encodage
                        print(f"    - {badge['name']} (+{badge['points']} XP)")
                else:
                    print("  [INFO] Aucun badge attribue pour le moment")
            except Exception as e:
                print(f"  [ERROR] Erreur: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("MIGRATION TERMINEE")
    print("=" * 80)


if __name__ == '__main__':
    migrate_badges()
