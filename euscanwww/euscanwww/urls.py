from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^', include('djeuscan.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('euscan_accounts.urls')),
    url(r'^accounts/', include('euscan_captcha.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
)


if settings.DEBUG:
    import os

    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.join(settings.EUSCAN_ROOT, 'htdocs'),
        }),
    )
