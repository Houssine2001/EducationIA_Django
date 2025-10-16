from django import template
import json

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplie deux valeurs"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value):
    """Convertit en pourcentage"""
    try:
        return float(value) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire"""
    return dictionary.get(key)

@register.filter
def jsonify(obj):
    """Convertit en JSON pour JavaScript"""
    return json.dumps(obj)