from django import template
from webui.models import VIRULENCE_FACTORS

register = template.Library()

@register.filter
def virulence_factor_str(value):
    for v in VIRULENCE_FACTORS:
        if v == value:
            return  VIRULENCE_FACTORS[v]
       
    return "Unknown"

@register.filter
def no_virulence_factor_str(value):
    for v in VIRULENCE_FACTORS:
        if v == value:
            return  "No " + VIRULENCE_FACTORS[v].lower() + " found"
       
    return "Unknown"
