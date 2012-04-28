from django import template

register = template.Library()


def sub(value, arg=None):
    return value - arg

register.filter('sub', sub)
