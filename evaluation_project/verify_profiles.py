"""
Vérifier les profils utilisateurs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile

print("=== VERIFICATION DES PROFILS ===\n")

student_usernames = ['etudiant1', 'etudiant2', 'etudiant3']

for username in student_usernames:
    try:
        user = User.objects.get(username=username)
        print(f"✅ User: {username}")
        print(f"   - User ID: {user.id}")
        print(f"   - Email: {user.email}")
        
        # Vérifier avec userprofile (lowercase)
        try:
            profile = user.userprofile
            print(f"   - Profile exists: ✅ YES")
            print(f"   - Profile ID: {profile.id}")
            print(f"   - Profile role: {profile.role}")
        except Exception as e:
            print(f"   - Profile exists: ❌ NO")
            print(f"   - Error: {e}")
            
            # Essayer de créer le profil
            print(f"   - Tentative de création...")
            try:
                profile = UserProfile.objects.create(user=user, role='student')
                print(f"   - ✨ Profil créé avec succès! ID: {profile.id}")
            except Exception as create_error:
                print(f"   - ❌ Erreur création: {create_error}")
        
        print()
        
    except User.DoesNotExist:
        print(f"❌ User not found: {username}\n")

# Afficher tous les profils
print("\n=== TOUS LES PROFILS ===")
all_profiles = UserProfile.objects.all()
print(f"Total: {all_profiles.count()} profils")
for profile in all_profiles:
    print(f"  - {profile.user.username}: role={profile.role}, id={profile.id}")
