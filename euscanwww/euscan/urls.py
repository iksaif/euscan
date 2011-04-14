from django.conf.urls.defaults import *

urlpatterns = patterns('euscan.views',
    (r'^$', 'index'),
    (r'^logs/$', 'logs'),
    (r'^categories/$', 'categories'),
    (r'^category/(?P<category>[\w+][\w+.-]*)/packages/$', 'category'),
    (r'^herds/$', 'herds'),
    (r'^herd/(?P<herd>[\w+][\w+.-]*)/packages/$', 'herd'),
    (r'^maintainers/$', 'maintainers'),
    (r'^maintainer/(?P<maintainer_id>\d+)/packages/$', 'maintainer'),
    (r'^package/(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/$', 'package'),
)
