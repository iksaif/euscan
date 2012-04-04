from django import template
from django.utils.timesince import timesince
from django.conf import settings
from django.utils.timezone import make_aware, get_default_timezone
from datetime import datetime

register = template.Library()

def timedelta(value, arg=None):
    if not value:
        return ''
    if arg:
        cmp = arg
    else:
        cmp = datetime.now()
        if settings.USE_TZ:
            cmp = make_aware(cmp, get_default_timezone())
    if value > cmp:
        return "in %s" % timesince(cmp,value)
    else:
        return "%s ago" % timesince(value,cmp)

register.filter('timedelta',timedelta)
