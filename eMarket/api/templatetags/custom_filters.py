from django import template

register = template.Library()

@register.filter(name='trim')
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None
