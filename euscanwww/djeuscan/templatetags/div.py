from django import template

register = template.Library()

def div(value, arg=None):
    return float(value)/float(arg)

register.filter('div', div)
