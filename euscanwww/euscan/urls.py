from django.conf.urls.defaults import *

urlpatterns = patterns('euscan.views',
    (r'^$', 'index'),
    (r'^logs/$', 'logs'),
    (r'^world/$', 'world'),
    (r'^world/scan/$', 'world_scan'),
    (r'^categories/$', 'categories'),
    (r'^categories/(?P<category>[\w+][\w+.-]*)/view/$', 'category'),
    (r'^herds/$', 'herds'),
    (r'^herds/(?P<herd>[\{\}\w+.-]*)/view/$', 'herd'),
    (r'^maintainers/$', 'maintainers'),
    (r'^maintainers/(?P<maintainer_id>\d+)/view/$', 'maintainer'),
    (r'^package/(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/$', 'package'),
)
