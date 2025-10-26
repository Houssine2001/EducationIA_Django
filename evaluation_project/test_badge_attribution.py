#!/usr/bin/env python
import os
import sys

# Get the current directory (evaluation_project)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from evaluation.models import UserProfile
from evaluation.gamification import GamificationService

# Test pour etudiant1
print("=" * 60)
print("TEST ATTRIBUTION DE BADGES")
print("=" * 60)

profile = UserProfile.objects.get(user__username='etudiant1')
print(f"\nUtilisateur: {profile.user.username}")
print(f"Tests completes: {profile.total_tests_taken}")
print(f"Badges actuels: {len(profile.badges) if profile.badges else 0}")

# Réinitialiser
profile.badges = []
profile.total_xp = 0
profile.level = 1
profile.save()
print("\n[INFO] Profil reinitialise")

# Vérifier et attribuer les badges
gs = GamificationService(profile)
new_badges = gs.check_and_award_badges()

print(f"\n[SUCCESS] Badges attribues: {len(new_badges) if new_badges else 0}")
if new_badges:
    for badge in new_badges:
        print(f"  - {badge['name']} (+{badge['points']} XP)")
else:
    print("  [WARN] Aucun badge attribue")

# Recharger le profil
profile.refresh_from_db()
print(f"\n[RESULT] Total badges: {len(profile.badges) if profile.badges else 0}")
print(f"[RESULT] Total XP: {profile.total_xp}")
print(f"[RESULT] Level: {profile.level}")
print("\n" + "=" * 60)
