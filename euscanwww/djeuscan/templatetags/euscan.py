from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('euscan/_packages.html', takes_context=True)
def packages(context, pkgs):
    context['packages'] = pkgs
    return context


@register.inclusion_tag('euscan/_package_cols.html', takes_context=True)
def package_cols(context, infos):
    context['infos'] = infos
    return context


@register.inclusion_tag('euscan/_package_bar.html', takes_context=True)
def package_bar(context, infos):
    context['infos'] = infos
    return context


@register.inclusion_tag('euscan/_categories_table.html')
def categories_table(categories, extras=False):
    return {
        "categories": categories,
        "extras": extras,
        "STATIC_URL": settings.STATIC_URL,
    }


@register.inclusion_tag('euscan/_herds_table.html')
def herds_table(herds, extras=False):
    return {
        "herds": herds,
        "extras": extras,
        "STATIC_URL": settings.STATIC_URL,
    }


@register.inclusion_tag('euscan/_maintainers_table.html')
def maintainers_table(maintainers, extras=False):
    return {
        "maintainers": maintainers,
        "extras": extras,
        "STATIC_URL": settings.STATIC_URL,
    }


@register.inclusion_tag('euscan/_overlays_table.html')
def overlays_table(overlays):
    return {
        "overlays": overlays,
        "STATIC_URL": settings.STATIC_URL,
    }
