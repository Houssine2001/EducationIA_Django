"""
Backend d'authentification personnalisé pour permettre la connexion avec email
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Permet la connexion avec l'email au lieu du username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Chercher l'utilisateur par email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Si pas trouvé par email, essayer par username (fallback)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        
        # Vérifier le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
