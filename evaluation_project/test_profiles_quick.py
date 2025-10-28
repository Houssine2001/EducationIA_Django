from django.contrib.auth.models import User
from evaluation.utils import get_or_create_user_profile_safe

print("=" * 60)
print("TEST DES PROFILS")
print("=" * 60)

for username in ['etudiant1', 'etudiant3']:
    try:
        user = User.objects.get(username=username)
        profile = get_or_create_user_profile_safe(user)
        print(f"✅ {username}:")
        print(f"   Level: {profile.level}")
        print(f"   XP: {profile.total_xp}")
        print(f"   Role: {profile.role}")
    except Exception as e:
        print(f"❌ {username}: {e}")

print("=" * 60)
