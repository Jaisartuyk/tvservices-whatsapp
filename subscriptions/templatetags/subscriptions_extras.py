from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtro personalizado para acceder a valores de diccionario en plantillas"""
    return dictionary.get(key, '')

@register.filter
def abs_value(value):
    """Filtro para obtener el valor absoluto de un número"""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return 0