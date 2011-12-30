from annoying.decorators import render_to
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max

from euscan.models import Version, Package, Herd, Maintainer, EuscanResult, VersionLog
from euscan.forms import WorldForm, PackagesForm

import charts

""" Views """

@render_to('euscan/index.html')
def index(request):
    ctx = {}
    ctx['n_packaged'] = charts.xint(Package.objects.aggregate(Sum('n_packaged'))['n_packaged__sum'])
    ctx['n_overlay'] = charts.xint(Package.objects.aggregate(Sum('n_overlay'))['n_overlay__sum'])
    ctx['n_versions'] = charts.xint(Package.objects.aggregate(Sum('n_versions'))['n_versions__sum'])
    ctx['n_upstream'] = ctx['n_versions'] - ctx['n_packaged'] - ctx['n_overlay']
    ctx['n_packages'] = Package.objects.count()
    ctx['n_herds'] = Herd.objects.count()
    ctx['n_maintainers'] = Maintainer.objects.count()
    ctx['last_scan'] = EuscanResult.objects.get(id=EuscanResult.objects.aggregate(Max('id'))['id__max']).datetime
    return ctx

@render_to('euscan/logs.html')
def logs(request):
    return {}

@render_to('euscan/categories.html')
def categories(request):
    categories = Package.objects.values('category').annotate(n_packaged=Sum('n_packaged'),
                                                             n_overlay=Sum('n_overlay'),
                                                             n_versions=Sum('n_versions'))

    return { 'categories' : categories }

@render_to('euscan/category.html')
def category(request, category):
    packages = Package.objects.filter(category=category)
    if not packages:
        raise Http404
    return { 'category' : category, 'packages' : packages }

@render_to('euscan/herds.html')
def herds(request):
    # FIXME: optimize the query, it uses 'LEFT OUTER JOIN' instead of 'INNER JOIN'
    herds = Package.objects.filter(herds__isnull=False)
    herds = herds.values('herds__herd').annotate(n_packaged=Sum('n_packaged'),
                                            n_overlay=Sum('n_overlay'),
                                            n_versions=Sum('n_versions'))
    return { 'herds' : herds }

@render_to('euscan/herd.html')
def herd(request, herd):
    herd = get_object_or_404(Herd, herd=herd)
    packages = Package.objects.filter(herds__id=herd.id)
    return { 'herd' : herd, 'packages' : packages }

@render_to('euscan/maintainers.html')
def maintainers(request):
    maintainers = Package.objects.filter(maintainers__isnull=False)
    maintainers = maintainers.values('maintainers__id', 'maintainers__name', 'maintainers__email')
    maintainers = maintainers.annotate(n_packaged=Sum('n_packaged'),
                                       n_overlay=Sum('n_overlay'),
                                       n_versions=Sum('n_versions'))

    return { 'maintainers' : maintainers }

@render_to('euscan/maintainer.html')
def maintainer(request, maintainer_id):
    maintainer = get_object_or_404(Maintainer, id=maintainer_id)
    packages = Package.objects.filter(maintainers__id=maintainer.id)
    return { 'maintainer' : maintainer, 'packages' : packages }

@render_to('euscan/overlays.html')
def overlays(request):
    overlays = Package.objects.values('version__overlay')
    overlays = overlays.exclude(version__overlay='')
    overlays = overlays.distinct()
    return { 'overlays' : overlays }

@render_to('euscan/overlay.html')
def overlay(request, overlay):
    packages = Package.objects.values('id', 'name', 'category',
                                      'n_versions', 'n_packaged',
                                      'n_overlay')
    packages = packages.filter(version__overlay=overlay).distinct()
    if not packages:
        raise Http404
    return { 'overlay' : overlay, 'packages' : packages }

@render_to('euscan/package.html')
def package(request, category, package):
    package = get_object_or_404(Package, category=category, name=package)
    package.homepages = package.homepage.split(' ')
    packaged = Version.objects.filter(package=package, packaged=True)
    upstream = Version.objects.filter(package=package, packaged=False)
    log = EuscanResult.objects.filter(package=package).order_by('-datetime')[:1]
    log = log[0] if log else None
    vlog = VersionLog.objects.filter(package=package).order_by('-id')
    return { 'package' : package, 'packaged' : packaged,
             'upstream' : upstream, 'log' : log, 'vlog' : vlog }

@render_to('euscan/world.html')
def world(request):
    world_form = WorldForm()
    packages_form = PackagesForm()

    return { 'world_form' : world_form,
             'packages_form' : packages_form }

@render_to('euscan/world_scan.html')
def world_scan(request):
    packages = []

    if 'world' in request.FILES:
        data = request.FILES['world'].read()
    elif 'packages' in request.POST:
        data = request.POST['packages']
    else:
        data = ""

    data = data.replace("\r", "")

    for pkg in data.split('\n'):
        try:
            if '/' in pkg:
                cat, pkg = pkg.split('/')
                packages.extend(Package.objects.filter(category=cat, name=pkg))
            else:
                packages.extend(Package.objects.filter(name=pkg))
        except:
            pass

    return { 'packages' : packages }


@render_to("euscan/about.html")
def about(request):
    return {}

@render_to("euscan/api.html")
def api(request):
    return {}

@render_to("euscan/statistics.html")
def statistics(request):
    return {}

def chart(request, **kwargs):
    from django.views.static import serve

    chart = kwargs['chart'] if 'chart' in kwargs else None

    if 'maintainer_id' in kwargs:
        kwargs['maintainer'] = get_object_or_404(Maintainer, id=kwargs['maintainer_id'])
    if 'herd' in kwargs:
        kwargs['herd'] = get_object_or_404(Herd, herd=kwargs['herd'])

    for kw in ('-small', '-weekly', '-monthly', '-yearly'):
        if chart.endswith(kw):
            if kw in ('-weekly', '-monthly', '-yearly'):
                kwargs['period'] = kw
            kwargs[kw] = True
            chart = chart[:-len(kw)]

    if chart == 'pie-packages':
        path = charts.pie_packages(**kwargs)
    elif chart == 'pie-versions':
        path = charts.pie_versions(**kwargs)
    elif chart == 'packages':
        path = charts.packages(**kwargs)
    elif chart == 'versions':
        path = charts.versions(**kwargs)
    else:
        raise Http404()

    return serve(request, path, document_root=charts.CHARTS_ROOT)

def chart_maintainer(request, **kwargs):
    return chart(request, **kwargs)

def chart_herd(request, **kwargs):
    return chart(request, **kwargs)

def chart_category(request, **kwargs):
    return chart(request, **kwargs)
