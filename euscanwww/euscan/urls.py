from django.conf.urls.defaults import *
from feeds import *

package_patterns = patterns('euscan.views',
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/feed/$', PackageFeed(), name='package_feed'),
    (r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/$', 'package'),
)

categories_patterns = patterns('euscan.views',
    (r'^(?P<category>[\w+][\w+.-]*)/(view/)?$', 'category'),
    url(r'^(?P<category>[\w+][\w+.-]*)/feed/$', CategoryFeed(), name='category_feed'),
    (r'^(?P<category>[\w+][\w+.-]*)/charts/(?P<chart>[\w\-]+).png$', 'chart_category'),
    (r'^$', 'categories'),
)

herds_patterns = patterns('euscan.views',
    (r'^(?P<herd>[\@\{\}\w+.-]*)/(view/)?$', 'herd'),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/feed/$', HerdFeed(), name='herd_feed'),
    (r'^(?P<herd>[\@\{\}\w+.-]*)/charts/(?P<chart>[\w\-]+).png$', 'chart_herd'),
    (r'^$', 'herds'),
)

maintainers_patterns = patterns('euscan.views',
    (r'^(?P<maintainer_id>\d+)/(view/)?$', 'maintainer'),
    url(r'^(?P<maintainer_id>\d+)/feed/$', MaintainerFeed(), name='maintainer_feed'),
    (r'^(?P<maintainer_id>\d+)/charts/(?P<chart>[\w\-]+).png$', 'chart_maintainer'),
    (r'^$', 'maintainers'),
)

urlpatterns = patterns('euscan.views',
    # Global stuff
    (r'^$', 'index'),
    url(r'^feed/$', GlobalFeed(), name='global_feed'),
    (r'^about/$', 'about'),
    (r'^statistics/$', 'statistics'),
    (r'^statistics/charts/(?P<chart>[\w\-]+).png$', 'chart'),
    (r'^world/$', 'world'),
    (r'^world/scan/$', 'world_scan'),

    # Real data
    (r'^categories/', include(categories_patterns)),
    (r'^herds/', include(herds_patterns)),
    (r'^maintainers/', include(maintainers_patterns)),
    (r'^package/', include(package_patterns)),
)
