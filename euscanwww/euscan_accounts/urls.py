from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

from euscan_accounts.feeds import UserFeed


urlpatterns = patterns('euscan_accounts.views',
    url(r'^profile/$', 'accounts_index', name="accounts_index"),
    url(r'^profile/preferences/$', 'accounts_preferences',
        name="accounts_preferences"),
    url(r'^categories/$', 'accounts_categories', name="accounts_categories"),
    url(r'^herds/$', 'accounts_herds', name="accounts_herds"),
    url(r'^maintainers/$', 'accounts_maintainers',
        name="accounts_maintainers"),
    url(r'^packages/$', 'accounts_packages', name="accounts_packages"),
    url(r'^overlays/$', 'accounts_overlays', name="accounts_overlays"),

    url(r'^feed/$', login_required(UserFeed()), name='user_feed'),

    url(r'^logout/$', logout, {'next_page': '/'}),

    url(r'^password/change/done/$',
        RedirectView.as_view(url="../../../profile/")),
)
