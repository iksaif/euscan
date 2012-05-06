from django.conf.urls.defaults import url, patterns, include
from feeds import PackageFeed, CategoryFeed, HerdFeed, MaintainerFeed, \
    GlobalFeed

package_patterns = patterns('djeuscan.views',
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/feed/$',
        PackageFeed(), name='package_feed'),
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/$',
        'package', name="package"),
)

categories_patterns = patterns('djeuscan.views',
    url(r'^(?P<category>[\w+][\w+.-]*)/(view/)?$', 'category',
        name="category"),
    url(r'^(?P<category>[\w+][\w+.-]*)/feed/$', CategoryFeed(),
        name='category_feed'),
    url(r'^(?P<category>[\w+][\w+.-]*)/charts/(?P<chart>[\w\-]+).png$',
        'chart_category', name="chart_category"),
    url(r'^$', 'categories', name="categories"),
)

herds_patterns = patterns('djeuscan.views',
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/(view/)?$', 'herd', name="herd"),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/feed/$', HerdFeed(), name='herd_feed'),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/charts/(?P<chart>[\w\-]+).png$',
        'chart_herd', name="chart_herd"),
    url(r'^$', 'herds', name="herds"),
)

maintainers_patterns = patterns('djeuscan.views',
    url(r'^(?P<maintainer_id>\d+)/(view/)?$', 'maintainer', name="maintainer"),
    url(r'^(?P<maintainer_id>\d+)/feed/$', MaintainerFeed(),
        name='maintainer_feed'),
    url(r'^(?P<maintainer_id>\d+)/charts/(?P<chart>[\w\-]+).png$',
        'chart_maintainer', name="chart_maintainer"),
    url(r'^$', 'maintainers', name="maintainers"),
)

overlays_patterns = patterns('djeuscan.views',
    url(r'^(?P<overlay>[\w+][\w+.-]*)/(view/)?$', 'overlay', name="overlay"),
    url(r'^$', 'overlays', name="overlays"),
)

urlpatterns = patterns('djeuscan.views',
    # Global stuff
    url(r'^api/', include('djeuscan.api.urls')),

    url(r'^$', 'index', name="index"),
    url(r'^feed/$', GlobalFeed(), name='global_feed'),
    url(r'^about/$', 'about', name="about"),
    url(r'^about/api$', 'api', name="api"),
    url(r'^statistics/$', 'statistics', name="statistics"),
    url(r'^statistics/charts/(?P<chart>[\w\-]+).png$', 'chart', name="chart"),
    url(r'^world/$', 'world', name="world"),
    url(r'^world/scan/$', 'world_scan', name="world_scan"),

    # Real data
    url(r'^categories/', include(categories_patterns)),
    url(r'^herds/', include(herds_patterns)),
    url(r'^maintainers/', include(maintainers_patterns)),
    url(r'^overlays/', include(overlays_patterns)),
    url(r'^package/', include(package_patterns)),
)
