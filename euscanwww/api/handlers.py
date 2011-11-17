from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc, HttpStatusCode

from django.db.models import Sum, Max
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from euscan.models import Version, Package, Herd, Maintainer, EuscanResult, VersionLog
from euscan.forms import WorldForm, PackagesForm

def xint(i):
    try:
        return int(i)
    except:
        return 0

def renameFields(vqs, fields):
    ret = []
    for n in vqs:
        for tr in fields:
            if tr[0] in n:
                n[tr[1]] = n[tr[0]]
                del n[tr[0]]
        ret.append(n)
    return ret

class catch_and_return(object):
    def __init__(self, err, response):
        self.err = err
        self.response = response

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except self.err:
                return self.response
        return wrapper

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
        data['n_packaged'] = xint(Package.objects.aggregate(Sum('n_packaged'))['n_packaged__sum'])
        data['n_overlay'] = xint(Package.objects.aggregate(Sum('n_overlay'))['n_overlay__sum'])
        data['n_versions'] = xint(Package.objects.aggregate(Sum('n_versions'))['n_versions__sum'])
        data['n_upstream'] = data['n_versions'] - data['n_packaged'] - data['n_overlay']
        data['n_packages'] = Package.objects.count()
        data['n_herds'] = Herd.objects.count()
        data['n_maintainers'] = Maintainer.objects.count()
        data['last_scan'] = EuscanResult.objects.get(id=EuscanResult.objects.aggregate(Max('id'))['id__max']).datetime

        return data

# /api/1.0/maintainers
class MaintainersHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        maintainers = Package.objects.filter(maintainers__isnull=False)
        maintainers = maintainers.values('maintainers__id', 'maintainers__name', 'maintainers__email')
        maintainers = maintainers.annotate(n_packaged=Sum('n_packaged'),
                                           n_overlay=Sum('n_overlay'),
                                           n_versions=Sum('n_versions'))

        maintainers = renameFields(maintainers, [('maintainers__id', 'id'),
                                                 ('maintainers__name', 'name'),
                                                 ('maintainers__email', 'email')])
        return maintainers

# /api/1.0/herds
class HerdsHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        # FIXME: optimize the query, it uses 'LEFT OUTER JOIN' instead of 'INNER JOIN'
        herds = Package.objects.filter(herds__isnull=False)
        herds = herds.values('herds__herd').annotate(n_packaged=Sum('n_packaged'),
                                                     n_overlay=Sum('n_overlay'),
                                                     n_versions=Sum('n_versions'))

        herds = renameFields(herds, [('herds__herd', 'herd')])
        return herds

# /api/1.0/categories
class CategoriesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        categories = Package.objects.values('category')
        categories = categories.annotate(n_packaged=Sum('n_packaged'),
                                         n_overlay=Sum('n_overlay'),
                                         n_versions=Sum('n_versions'))

        return categories

# /api/1.0/packages/by-maintainer/
# /api/1.0/packages/by-category/
# /api/1.0/packages/by-herd/
class PackagesHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('category', 'name', 'n_packaged', 'n_overlay', 'n_versions')
    model = Package

    @catch_and_return(ObjectDoesNotExist, rc.NOT_FOUND)
    def read(self, request, **kwargs):
        data = {}

        if 'category' in kwargs:
            packages = Package.objects.filter(category=kwargs['category'])
            data = { 'category' : kwargs['category'], 'packages' : packages }
        elif 'herd' in kwargs:
            herd = Herd.objects.get(herd=kwargs['herd'])
            packages = Package.objects.filter(herds__id=herd.id)
            data = { 'herd' : herd, 'packages' : packages }
        elif 'maintainer_id' in kwargs:
            maintainer = Maintainer.objects.get(id=kwargs['maintainer_id'])
            packages = Package.objects.filter(maintainers__id=maintainer.id)
            data = { 'maintainer' : maintainer, 'packages' : packages }

        if not data:
            return rc.NOT_FOUND

        return data

# /api/1.0/package/
class PackageHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    @catch_and_return(ObjectDoesNotExist, rc.NOT_FOUND)
    def read(self, request, category, package):
        package = Package.objects.get(category=category, name=package)
        package.homepages = package.homepage.split(' ')
        versions = Version.objects.filter(package=package)
        log = EuscanResult.objects.filter(package=package).order_by('-datetime')[:1]
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
            v = model_to_dict(v, ['version', 'revision', 'slot', 'overlay', 'datetime', 'action'])
            if v['action'] == VersionLog.VERSION_ADDED:
                v['action'] = 'added'
            if v['action'] == VersionLog.VERSION_REMOVED:
                v['action'] = 'removed'
            version_log.append(v)

        upstream = []
        packaged = []
        for version in versions:
            unpackaged = not version.packaged
            version = model_to_dict(version, ['version', 'revision', 'slot', 'overlay', 'urls'])
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

