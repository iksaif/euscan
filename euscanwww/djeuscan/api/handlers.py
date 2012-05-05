from piston.handler import AnonymousBaseHandler
from piston.utils import rc

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from djeuscan.models import Version, Package, Herd, Maintainer, EuscanResult, \
    VersionLog
from djeuscan.helpers import catch_and_return

# replace default XMLEmitter with ours
from piston.emitters import Emitter
from .emitters import EuscanXMLEmitter
Emitter.register('xml', EuscanXMLEmitter, 'text/xml; charset=utf-8')


# /api/1.0/
class RootHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        return {'api-version': '1.0'}


# /api/1.0/statistics
class StatisticsHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        data = {}
        data['n_packaged'] = Package.objects.n_packaged()
        data['n_overlay'] = Package.objects.n_overlay()
        data['n_versions'] = Package.objects.n_versions()
        data['n_upstream'] = Package.objects.n_upstream()
        data['n_packages'] = Package.objects.count()
        data['n_herds'] = Herd.objects.count()
        data['n_maintainers'] = Maintainer.objects.count()
        data['last_scan'] = EuscanResult.objects.latest().datetime

        return data


# /api/1.0/maintainers
class MaintainersHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        maintainers = Package.objects.maintainers(rename=True)

        return {'maintainers': maintainers}


# /api/1.0/herds
class HerdsHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        # FIXME: optimize the query, it uses 'LEFT OUTER JOIN'
        # instead of 'INNER JOIN'
        herds = Package.objects.herds(rename=True)

        return {'herds': herds}


# /api/1.0/categories
class CategoriesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        categories = Package.objects.categories()

        return {'categories': categories}


# /api/1.0/packages/by-maintainer/
# /api/1.0/packages/by-category/
# /api/1.0/packages/by-herd/
class PackagesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('category', 'name', 'n_packaged', 'n_overlay', 'n_versions',
              ('last_version_gentoo', ('version',)),
              ('last_version_overlay', ('version',)),
              ('last_version_upstream', ('version',)))
    model = Package

    @catch_and_return(ObjectDoesNotExist, rc.NOT_FOUND)
    def read(self, request, **kwargs):
        data = {}

        if 'category' in kwargs:
            packages = Package.objects.for_category(kwargs['category'])
            data = {'category': kwargs['category']}
        elif 'herd' in kwargs:
            herd = Herd.objects.get(herd=kwargs['herd'])
            packages = Package.objects.for_herd(herd)
            data = {'herd': herd}
        elif 'maintainer_id' in kwargs:
            maintainer = Maintainer.objects.get(id=kwargs['maintainer_id'])
            packages = Package.objects.for_maintainer(maintainer)
            data = {'maintainer': maintainer}

        data['packages'] = packages

        if not data:
            return rc.NOT_FOUND

        return data


# /api/1.0/package/
class PackageHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    @catch_and_return(ObjectDoesNotExist, rc.NOT_FOUND)
    def read(self, request, category, package):
        package = Package.objects.get(category=category, name=package)

        versions = Version.objects.filter(package=package)

        log = EuscanResult.objects.filter(package=package).\
                order_by('-datetime')[:1]
        log = log[0] if log else None

        vlog = VersionLog.objects.filter(package=package).order_by('-id')

        herds = []
        for herd in package.herds.all():
            herds.append(model_to_dict(herd, ['herd']))

        maintainers = []
        for maintainer in package.maintainers.all():
            maintainers.append(model_to_dict(maintainer, ['name', 'email']))

        version_log = []
        for v in vlog:
            v = model_to_dict(v, ['version', 'revision', 'slot', 'overlay',
                              'datetime', 'action'])
            if v['action'] == VersionLog.VERSION_ADDED:
                v['action'] = 'added'
            if v['action'] == VersionLog.VERSION_REMOVED:
                v['action'] = 'removed'
            version_log.append(v)

        upstream = []
        packaged = []
        for version in versions:
            unpackaged = not version.packaged
            version = model_to_dict(
                version,
                ['version', 'revision', 'slot', 'overlay', 'urls']
            )
            if unpackaged:
                upstream.append(version)
            else:
                packaged.append(version)

        package = model_to_dict(package, ['category', 'name', 'description',
                                          'homepage'])
        package['herds'] = herds
        package['maintainers'] = maintainers
        package['packaged'] = packaged
        package['upstream'] = upstream
        package['vlog'] = version_log
        if log:
            package['log'] = model_to_dict(log, ['result', 'datetime'])

        return package
