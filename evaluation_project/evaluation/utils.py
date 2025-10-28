"""
Fonctions utilitaires pour l'application evaluation
"""
from django.contrib.auth.models import User


def get_or_create_user_profile_safe(user):
    """
    Récupère ou crée le profil utilisateur de manière sécurisée.
    Gère les cas de profils dupliqués en retournant le plus récent.
    
    Args:
        user (User): L'utilisateur Django
        
    Returns:
        UserProfile: Le profil utilisateur (le plus récent si duplicatas)
    """
    from .models import UserProfile
    
    # Récupérer le profil le plus récent s'il existe
    profile = UserProfile.objects.filter(user=user).order_by('-created_at').first()
    
    if not profile:
        # Créer un nouveau profil si aucun n'existe
        profile = UserProfile.objects.create(
            user=user,
            level='intermediate'  # Niveau par défaut
        )
    
    return profile


def validate_score(score):
    """
    Valide qu'un score est dans la plage acceptable (0-100)
    
    Args:
        score (float): Score à valider
        
    Returns:
        bool: True si le score est valide, False sinon
    """
    try:
        score = float(score)
        return 0 <= score <= 100
    except (ValueError, TypeError):
        return False


def calculate_average(scores):
    """
    Calcule la moyenne d'une liste de scores
    
    Args:
        scores (list): Liste de scores numériques
        
    Returns:
        float: Moyenne des scores ou 0 si liste vide
    """
    if not scores:
        return 0
    return sum(scores) / len(scores)


def format_performance_data(data):
    """
    Formate les données de performance pour l'affichage
    
    Args:
        data (dict): Données brutes de performance
        
    Returns:
        dict: Données formatées
    """
    # À implémenter selon vos besoins
    return data
