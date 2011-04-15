from django import template

register = template.Library()

@register.inclusion_tag('euscan/_packages.html')
def packages(packages):
    return { 'packages' : packages }
