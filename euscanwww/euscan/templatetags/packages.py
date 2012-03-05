from django import template

register = template.Library()

@register.inclusion_tag('euscan/_packages.html', takes_context=True)
def packages(context, packages):
    context['packages'] = packages
    return context

@register.inclusion_tag('euscan/_package_cols.html', takes_context=True)
def package_cols(context, infos):
    context['infos'] = infos
    return context

@register.inclusion_tag('euscan/_package_bar.html', takes_context=True)
def package_bar(context, infos):
    context['infos'] = infos
    return context
