from django.conf.urls.defaults import url, patterns, include
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import logout
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

from djcelery.views import apply as apply_task
from djeuscan.views import registered_tasks

from djeuscan.feeds import PackageFeed, CategoryFeed, HerdFeed, \
    MaintainerFeed, GlobalFeed, UserFeed, WorldScanFeed


admin_required = user_passes_test(lambda u: u.is_superuser)


package_patterns = patterns('djeuscan.views',
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/feed/$',
        PackageFeed(), name='package_feed'),
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/$',
        'package', name="package"),
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/favourite/$',
        'favourite_package', name="favourite_package"),
    url((r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/'
         'unfavourite/$'), 'unfavourite_package', name="unfavourite_package"),
    url((r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/'
         'refresh$'), "refresh_package", name="refresh_package"),
    url(r'^(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/problem$',
        'problem', name="problem"),
)

categories_patterns = patterns('djeuscan.views',
    url(r'^(?P<category>[\w+][\w+.-]*)/(view/)?$', 'category',
        name="category"),
    url(r'^(?P<category>[\w+][\w+.-]*)/feed/$', CategoryFeed(),
        name='category_feed'),
    url(r'^(?P<category>[\w+][\w+.-]*)/charts/(?P<chart>[\w\-]+).png$',
        'chart_category', name="chart_category"),
    url(r'^(?P<category>[\w+][\w+.-]*)/favourite/$',
        'favourite_category', name="favourite_category"),
    url(r'^(?P<category>[\w+][\w+.-]*)/unfavourite/$',
        'unfavourite_category', name="unfavourite_category"),
    url(r'^$', 'categories', name="categories"),
)

herds_patterns = patterns('djeuscan.views',
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/(view/)?$', 'herd', name="herd"),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/feed/$', HerdFeed(), name='herd_feed'),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/charts/(?P<chart>[\w\-]+).png$',
        'chart_herd', name="chart_herd"),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/favourite/$', 'favourite_herd',
        name="favourite_herd"),
    url(r'^(?P<herd>[\@\{\}\w+.-]*)/unfavourite/$', 'unfavourite_herd',
        name="unfavourite_herd"),
    url(r'^$', 'herds', name="herds"),
)

maintainers_patterns = patterns('djeuscan.views',
    url(r'^(?P<maintainer_id>\d+)/(view/)?$', 'maintainer', name="maintainer"),
    url(r'^(?P<maintainer_id>\d+)/feed/$', MaintainerFeed(),
        name='maintainer_feed'),
    url(r'^(?P<maintainer_id>\d+)/charts/(?P<chart>[\w\-]+).png$',
        'chart_maintainer', name="chart_maintainer"),
    url(r'^(?P<maintainer_id>\d+)/favourite/$',
        'favourite_maintainer', name="favourite_maintainer"),
    url(r'^(?P<maintainer_id>\d+)/unfavourite/$',
        'unfavourite_maintainer', name="unfavourite_maintainer"),
    url(r'^$', 'maintainers', name="maintainers"),
)

overlays_patterns = patterns('djeuscan.views',
    url(r'^(?P<overlay>[\w+][\w+.-]*)/(view/)?$', 'overlay', name="overlay"),
    url(r'^(?P<overlay>[\w+][\w+.-]*)/favourite/$', 'favourite_overlay',
        name="favourite_overlay"),
    url(r'^(?P<overlay>[\w+][\w+.-]*)/unfavourite/$', 'unfavourite_overlay',
        name="unfavourite_overlay"),
    url(r'^$', 'overlays', name="overlays"),
)

tasks_patterns = patterns('djeuscan.views',
    url(r'^registered_tasks/$', admin_required(registered_tasks),
        name="registered_tasks"),
    url(r'^apply/(?P<task_name>.*)/$', admin_required(apply_task),
        name="apply_task"),
)

accounts_patterns = patterns('djeuscan.views',
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


urlpatterns = patterns('djeuscan.views',
    # Global stuff
    url(r'^api/', include('djeuscan.api.urls')),

    url(r'^$', 'index', name="index"),
    url(r'^feed/$', GlobalFeed(), name='global_feed'),
    url(r'^about/$', 'about', name="about"),
    url(r'^about/api$', 'api', name="api"),
    url(r'^about/feeds$', 'feeds', name="feeds"),
    url(r'^about/config$', 'config', name="config"),
    url(r'^statistics/$', 'statistics', name="statistics"),
    url(r'^statistics/charts/(?P<chart>[\w\-]+).png$', 'chart', name="chart"),
    url(r'^world/$', 'world', name="world"),
    url(r'^world/scan/$', 'world_scan', name="world_scan"),
    url(r'^world/scan/feed$', WorldScanFeed(), name="world_scan_feed"),
    url(r'^world/favourite/$', 'favourite_world', name="favourite_world"),
    url(r'^world/unfavourite/$', 'unfavourite_world',
        name="unfavourite_world"),

    # Real data
    url(r'^categories/', include(categories_patterns)),
    url(r'^herds/', include(herds_patterns)),
    url(r'^maintainers/', include(maintainers_patterns)),
    url(r'^overlays/', include(overlays_patterns)),
    url(r'^package/', include(package_patterns)),

    url(r'^tasks/', include(tasks_patterns)),
    url(r'^accounts/', include(accounts_patterns)),
)
