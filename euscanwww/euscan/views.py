from annoying.decorators import render_to
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max

from euscan.models import Version, Package, Herd, Maintainer, EuscanResult
from euscan.forms import WorldForm, PackagesForm

@render_to('euscan/index.html')
def index(request):
    ctx = {}
    ctx['n_packaged'] = Package.objects.aggregate(Sum('n_packaged'))['n_packaged__sum']
    ctx['n_versions'] = Package.objects.aggregate(Sum('n_versions'))['n_versions__sum']
    if ctx['n_versions'] is not None and ctx['n_packaged'] is not None:
        ctx['n_upstream'] = ctx['n_versions'] - ctx['n_packaged']
    ctx['n_packages'] = Package.objects.count()
    ctx['n_herds'] = Herd.objects.count()
    ctx['n_maintainers'] = Maintainer.objects.count()
    ctx['last_scan'] = EuscanResult.objects.aggregate(Max('datetime'))['datetime__max']
    return ctx

@render_to('euscan/logs.html')
def logs(request):
    return {}

@render_to('euscan/categories.html')
def categories(request):
    categories = Package.objects.values('category').annotate(n_packaged=Sum('n_packaged'), n_versions=Sum('n_versions'))
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
    herds = Package.objects.filter(herds__isnull=False).values('herds__herd').annotate(n_packaged=Sum('n_packaged'), n_versions=Sum('n_versions'))
    return { 'herds' : herds }

@render_to('euscan/herd.html')
def herd(request, herd):
    herd = get_object_or_404(Herd, herd=herd)
    packages = Package.objects.filter(herds__id=herd.id)
    return { 'herd' : herd, 'packages' : packages }

@render_to('euscan/maintainers.html')
def maintainers(request):
    maintainers = Package.objects.filter(maintainers__isnull=False).values('maintainers__id', 'maintainers__name').annotate(n_packaged=Sum('n_packaged'), n_versions=Sum('n_versions'))
    return { 'maintainers' : maintainers }

@render_to('euscan/maintainer.html')
def maintainer(request, maintainer_id):
    maintainer = get_object_or_404(Maintainer, id=maintainer_id)
    packages = Package.objects.filter(maintainers__id=maintainer.id)
    return { 'maintainer' : maintainer, 'packages' : packages }

@render_to('euscan/package.html')
def package(request, category, package):
    package = get_object_or_404(Package, category=category, name=package)
    packaged = Version.objects.filter(package=package, packaged=True)
    upstream = Version.objects.filter(package=package, packaged=False)
    log = EuscanResult.objects.filter(package=package).order_by('-datetime')[:1]
    log = log[0] if log else None
    return { 'package' : package, 'packaged' : packaged,
             'upstream' : upstream, 'log' : log }

@render_to('euscan/world.html')
def world(request):
    world_form = WorldForm()
    packages_form = PackagesForm()

    return { 'world_form' : world_form,
             'packages_form' : packages_form }

@render_to('euscan/world_scan.html')
def world_scan(request):
    packages = []

    # FIXME
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
    print packages

    return { 'packages' : packages }


