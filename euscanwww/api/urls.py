from django.conf.urls.defaults import *

from piston.resource import Resource
from api.handlers import *

root_handler = Resource(handler=RootHandler)
statistics_handler = Resource(handler=StatisticsHandler)
herds_handler = Resource(handler=HerdsHandler)
categories_handler = Resource(handler=CategoriesHandler)
maintainers_handler = Resource(handler=MaintainersHandler)
packages_handler = Resource(handler=PackagesHandler)
package_handler = Resource(handler=PackageHandler)

urlpatterns = patterns('api.views',
    (r'^1.0/statistics\.(?P<emitter_format>.+)$', statistics_handler),
    (r'^1.0/herds\.(?P<emitter_format>.+)$', herds_handler),
    (r'^1.0/categories\.(?P<emitter_format>.+)$', categories_handler),
    (r'^1.0/maintainers\.(?P<emitter_format>.+)$', maintainers_handler),

    (r'^1.0/packages/by-maintainer/(?P<maintainer_id>\d+)\.(?P<emitter_format>.+)$', packages_handler),
    (r'^1.0/packages/by-herd/(?P<herd>[\@\{\}\w+.-]*)\.(?P<emitter_format>.+)?$', packages_handler),
    (r'^1.0/packages/by-category/(?P<category>[\w+][\w+.-]*)\.(?P<emitter_format>.+)?$', packages_handler),
    (r'^1.0/package/(?P<category>[\w+][\w+.-]*)/(?P<package>[\w+][\w+.-]*)\.(?P<emitter_format>.+)$', package_handler),

    (r'^1.0/api\.(?P<emitter_format>.+)$', root_handler),
)
