from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('captcha.backends.default.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^', include('djeuscan.urls')),
)


if settings.DEBUG:
    import os

    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.join(settings.EUSCAN_ROOT, 'htdocs'),
        }),
    )
