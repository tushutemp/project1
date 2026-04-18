from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces and capitalize words"""
    if value:
        return value.replace('_', ' ').title()
    return value