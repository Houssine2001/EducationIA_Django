"""
Test de connexion avec le bon related_name
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=== TEST RELATED_NAME ===\n")

student_usernames = ['etudiant1', 'etudiant2', 'etudiant3']

for username in student_usernames:
    try:
        user = User.objects.get(username=username)
        print(f"✅ User: {username}")
        
        # Test avec .profile (correct)
        try:
            profile = user.profile
            print(f"   ✅ user.profile works!")
            print(f"   - Role: {profile.role}")
            print(f"   - Profile ID: {profile.id}")
        except Exception as e:
            print(f"   ❌ user.profile failed: {e}")
        
        # Test avec .userprofile (incorrect)
        try:
            profile = user.userprofile
            print(f"   ⚠️  user.userprofile works (not expected)")
        except Exception as e:
            print(f"   ✅ user.userprofile correctly fails: {type(e).__name__}")
        
        print()
        
    except User.DoesNotExist:
        print(f"❌ User not found: {username}\n")

print("✅ Le related_name est bien 'profile', pas 'userprofile'")
