from django import template
from webui.models import VIRULENCE_FACTORS, VIRULENCE_FACTOR_CATEGORIES

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

@register.filter
def vir_category(value):
    if value in VIRULENCE_FACTOR_CATEGORIES:
        return VIRULENCE_FACTOR_CATEGORIES[value]
    
    return 'Unknown'
