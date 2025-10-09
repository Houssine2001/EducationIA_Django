"""
Script pour créer les UserProfile manquants pour les comptes étudiants
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile

# Liste des étudiants
student_usernames = ['etudiant1', 'etudiant2', 'etudiant3']

print("🔍 Vérification des comptes étudiants...")
for username in student_usernames:
    try:
        user = User.objects.get(username=username)
        print(f"  ✅ Utilisateur trouvé: {username}")
        
        # Vérifier si le profil existe
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'student'}
        )
        
        if created:
            print(f"    ✨ Profil créé avec role='student'")
        else:
            # Mettre à jour le rôle si nécessaire
            if profile.role != 'student':
                profile.role = 'student'
                profile.save()
                print(f"    🔄 Rôle mis à jour: {profile.role}")
            else:
                print(f"    ℹ️  Profil existant avec role='{profile.role}'")
                
    except User.DoesNotExist:
        print(f"  ❌ Utilisateur non trouvé: {username}")

print("\n📊 Résumé final:")
profiles = UserProfile.objects.filter(user__username__in=student_usernames)
print(f"Total profils étudiants: {profiles.count()}")
for profile in profiles:
    print(f"  - {profile.user.username} → role={profile.role}")

print("\n✅ Opération terminée!")
