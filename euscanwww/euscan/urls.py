from django.conf.urls.defaults import *

urlpatterns = patterns('euscan.views',
    (r'^$', 'index'),
    (r'^logs/$', 'logs'),
    (r'^categories/$', 'categories'),
    (r'^category/(?P<category>\w+)/packages/$', 'category'),
    (r'^herds/$', 'herds'),
    (r'^herd/(?P<herd>\w+)/packages/$', 'herd'),
    (r'^maintainers/$', 'maintainers'),
    (r'^maintainer/(?P<maintainer_id>\d+)/packages/$', 'maintainer'),
    (r'^package/(?P<category>\w+)/(?P<package>\w+)/$', 'package'),
)
