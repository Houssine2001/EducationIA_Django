from django.apps import AppConfig


class EvaluationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evaluation'
    
    def ready(self):
        """
        Fix pour Djongo: Désactiver complètement update_last_login
        """
        # Importer et désactiver le signal
        import django.contrib.auth.models
        from django.contrib.auth import signals
        
        # Remplacer la fonction problématique par une version vide
        def dummy_update_last_login(sender, user, **kwargs):
            """Ne rien faire - éviter l'erreur Djongo"""
            pass
        
        # Déconnecter l'ancien signal
        try:
            signals.user_logged_in.disconnect(django.contrib.auth.models.update_last_login)
        except:
            pass
        
        # Connecter notre version vide
        signals.user_logged_in.connect(dummy_update_last_login)
