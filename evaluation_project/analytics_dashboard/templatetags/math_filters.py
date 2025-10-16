from django import template
import math

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value):
    """Converts a decimal to percentage."""
    try:
        return float(value) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def round_to(value, decimals):
    """Rounds value to specified number of decimals."""
    try:
        return round(float(value), int(decimals))
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def add_class(field, css_class):
    """Adds CSS class to form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary."""
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    """Subtracts arg from value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def abs_value(value):
    """Returns absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0