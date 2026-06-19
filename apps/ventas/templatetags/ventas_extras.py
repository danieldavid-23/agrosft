from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def abs_value(value):
    """Retorna el valor absoluto"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0
