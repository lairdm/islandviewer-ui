from django import template

register = template.Library()

@register.filter
def cleanfilename(value):
    return ''.join(e for e in value if e.isalnum())
