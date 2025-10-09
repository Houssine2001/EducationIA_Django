"""
Middleware pour patcher update_last_login et éviter l'erreur Djongo
"""
import django.contrib.auth.models
from django.contrib.auth import signals


class DjongoFixMiddleware:
    """
    Middleware qui patch update_last_login au premier appel
    """
    _patched = False
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Patcher une seule fois
        if not DjongoFixMiddleware._patched:
            self.patch_update_last_login()
            DjongoFixMiddleware._patched = True
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    @staticmethod
    def patch_update_last_login():
        """
        Désactiver complètement le signal update_last_login
        """
        # Déconnecter le signal existant
        try:
            signals.user_logged_in.disconnect(
                django.contrib.auth.models.update_last_login
            )
            print("✅ Signal update_last_login désactivé (Fix Djongo)")
        except Exception as e:
            print(f"⚠️  Impossible de déconnecter update_last_login: {e}")
