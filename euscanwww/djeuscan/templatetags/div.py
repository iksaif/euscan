from django import template

register = template.Library()


def div(value, arg=None):
    try:
        return float(value) / float(arg)
    except ZeroDivisionError:
        return 0

register.filter('div', div)
