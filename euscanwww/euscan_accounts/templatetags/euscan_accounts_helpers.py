from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.inclusion_tag('euscan/_favourite.html', takes_context=True)
def favourite_buttons(context, subj, *args):
    context["favourite_url"] = reverse("favourite_%s" % subj, args=args)
    context["unfavourite_url"] = reverse("unfavourite_%s" % subj, args=args)
    return context
