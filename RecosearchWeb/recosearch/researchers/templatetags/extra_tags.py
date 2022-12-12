from django import template

register = template.Library()

@register.filter
def renderScore(value):
    return "%"+ str(value)[0:4]
