from django import template

register = template.Library()

@register.inclusion_tag('euscan/_packages.html')
def packages(packages):
    return { 'packages' : packages }

@register.inclusion_tag('euscan/_package_cols.html')
def package_cols(infos):
    return { 'infos' : infos }

@register.inclusion_tag('euscan/_package_bar.html')
def package_bar(infos):
    return { 'infos' : infos }
