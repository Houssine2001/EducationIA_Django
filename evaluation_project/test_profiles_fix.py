from django.contrib.auth.models import User
from evaluation.utils import get_or_create_user_profile_safe
from evaluation.models import UserProfile

print("=" * 60)
print("VERIFICATION DES PROFILS")
print("=" * 60)

for username in ['etudiant1', 'etudiant3', 'houssine']:
    try:
        user = User.objects.get(username=username)
        count = UserProfile.objects.filter(user=user).count()
        profile = get_or_create_user_profile_safe(user)
        print(f"✅ {username}: {count} profil(s), role={profile.role}")
    except Exception as e:
        print(f"❌ {username}: ERREUR - {e}")
