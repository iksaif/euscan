from django import template
from django.conf import settings

from euscan.version import is_version_type_stable, get_version_type

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


@register.filter
def is_stable(version_type):
    return is_version_type_stable(version_type)


@register.filter
def version_type(version):
    return get_version_type(version)


@register.filter
def ansi_to_html(text):
    from ansi2html import Ansi2HTMLConverter
    conv = Ansi2HTMLConverter(inline=True, linkify=True)
    return conv.convert(text, full=False)
