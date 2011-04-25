from django import template

register = template.Library()

def div(value, arg=None):
    return value/arg

register.filter('div', div)
