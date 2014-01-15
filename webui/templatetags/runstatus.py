from django import template
from webui.models import STATUS_CHOICES

register = template.Library()

@register.filter
def get_status(value):
    for p in STATUS_CHOICES:
        if p[0] == value:
            return p[1]
    
    return "Unknown"

