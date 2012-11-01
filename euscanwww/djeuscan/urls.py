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
    url(r'^$', 'package', name="package"),
    url(r'^feed/$', PackageFeed(), name='package_feed'),
    url(r'^favourite/$', 'favourite_package', name="favourite_package"),
    url(r'^unfavourite/$', 'unfavourite_package', name="unfavourite_package"),
    url(r'^refresh$', "refresh_package", name="refresh_package"),
    url(r'^problem$', 'problem', name="problem"),
)

categories_patterns = patterns('djeuscan.views',
    url(r'^(?:view/)?$', 'category', name="category"),
    url(r'^feed/$', CategoryFeed(), name='category_feed'),
    url(r'^charts/(?P<chart>[\w\-]+).png$', 'chart_category',
        name="chart_category"),
    url(r'^favourite/$', 'favourite_category', name="favourite_category"),
    url(r'^unfavourite/$', 'unfavourite_category',
        name="unfavourite_category"),
)

herds_patterns = patterns('djeuscan.views',
    url(r'^(?:view/)?$', 'herd', name="herd"),
    url(r'^feed/$', HerdFeed(), name='herd_feed'),
    url(r'^charts/(?P<chart>[\w\-]+).png$', 'chart_herd', name="chart_herd"),
    url(r'^favourite/$', 'favourite_herd', name="favourite_herd"),
    url(r'^unfavourite/$', 'unfavourite_herd', name="unfavourite_herd"),
)

maintainers_patterns = patterns('djeuscan.views',
    url(r'^(?:view/)?$', 'maintainer', name="maintainer"),
    url(r'^feed/$', MaintainerFeed(), name='maintainer_feed'),
    url(r'^charts/(?P<chart>[\w\-]+).png$', 'chart_maintainer',
        name="chart_maintainer"),
    url(r'^favourite/$', 'favourite_maintainer', name="favourite_maintainer"),
    url(r'^unfavourite/$', 'unfavourite_maintainer',
        name="unfavourite_maintainer"),
)

overlays_patterns = patterns('djeuscan.views',
    url(r'^(?:view/)?$', 'overlay', name="overlay"),
    url(r'^favourite/$', 'favourite_overlay', name="favourite_overlay"),
    url(r'^unfavourite/$', 'unfavourite_overlay', name="unfavourite_overlay"),
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
    url(r'^categories/$', 'categories', name="categories"),
    url(r'^categories/(?P<category>[\w+][\w+.-]*)/',
        include(categories_patterns)),

    url(r'^herds/$', 'herds', name="herds"),
    url(r'^herds/(?P<herd>[\@\{\}\w+.-]+)/', include(herds_patterns)),

    url(r'^maintainers/$', 'maintainers', name="maintainers"),
    url(r'^maintainers/(?P<maintainer_id>\d+)/',
        include(maintainers_patterns)),
    url(r'^maintainers/(?P<maintainer_email>[^/]+)/',
        include(maintainers_patterns)),

    url(r'^overlays/$', 'overlays', name="overlays"),
    url(r'^overlays/(?P<overlay>[\w+][\w+.-]*)/', include(overlays_patterns)),

    url(r'^package/(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)/',
        include(package_patterns)),

    url(r'^tasks/', include(tasks_patterns)),
    url(r'^accounts/', include(accounts_patterns)),
)
