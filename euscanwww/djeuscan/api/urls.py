from django.conf.urls.defaults import url, patterns

from piston.resource import Resource
from handlers import RootHandler, StatisticsHandler, HerdsHandler, \
    CategoriesHandler, MaintainersHandler, PackagesHandler, PackageHandler

root_handler = Resource(handler=RootHandler)
statistics_handler = Resource(handler=StatisticsHandler)
herds_handler = Resource(handler=HerdsHandler)
categories_handler = Resource(handler=CategoriesHandler)
maintainers_handler = Resource(handler=MaintainersHandler)
packages_handler = Resource(handler=PackagesHandler)
package_handler = Resource(handler=PackageHandler)

urlpatterns = patterns('djeuscan.api.views',
    url(r'^1.0/statistics\.(?P<emitter_format>.+)$', statistics_handler,
        name='api.views.statistics'),
    url(r'^1.0/herds\.(?P<emitter_format>.+)$', herds_handler,
        name='api.views.herds'),
    url(r'^1.0/categories\.(?P<emitter_format>.+)$', categories_handler,
        name='api.views.categories'),
    url(r'^1.0/maintainers\.(?P<emitter_format>.+)$', maintainers_handler,
        name='api.views.maintainers'),

    url(r'^1.0/packages/by-maintainer/(?P<maintainer_id>\d+)\.(?P<emitter_format>.+)$',
        packages_handler, name='api.views.packages'),
    url(r'^1.0/packages/by-herd/(?P<herd>[\@\{\}\w+.-]*)\.(?P<emitter_format>.+)?$',
        packages_handler, name='api.views.packages'),
    url(r'^1.0/packages/by-category/(?P<category>[\w+][\w+.-]*)\.(?P<emitter_format>.+)?$',
        packages_handler, name='api.views.packages'),

    url(r'^1.0/package/(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)\.(?P<emitter_format>.+)$',
        package_handler, name='api.views.package'),

    url(r'^1.0/api\.(?P<emitter_format>.+)$',
        root_handler, name='api.views.root'),
)
