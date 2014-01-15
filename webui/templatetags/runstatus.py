from django import template
from webui.models import STATUS_CHOICES
import pprint

register = template.Library()

@register.filter
def get_status(value):
    pprint.pprint(STATUS_CHOICES)
    for p in STATUS_CHOICES:
        if p[0] == value:
            return p[1]
    
    return "Unknown"

