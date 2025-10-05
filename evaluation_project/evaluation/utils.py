"""
Fonctions utilitaires pour l'application evaluation
"""

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
