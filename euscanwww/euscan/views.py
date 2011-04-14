from annoying.decorators import render_to
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max

from euscan.models import Version, Package, Herd, Maintainer, EuscanResult

@render_to('euscan/index.html')
def index(request):
    ctx = {}
    ctx['n_packaged'] = Package.objects.aggregate(Sum('n_packaged'))['n_packaged__sum']
    ctx['n_versions'] = Package.objects.aggregate(Sum('n_versions'))['n_versions__sum']
    if ctx['n_versions'] is not None and ctx['n_pacaged'] is not None:
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
    return {}

@render_to('euscan/herd.html')
def herd(request, herd):
    return {}

@render_to('euscan/maintainers.html')
def maintainers(request):
    return {}

@render_to('euscan/maintainer.html')
def maintainer(request, maintainer_id):
    return {}

@render_to('euscan/package.html')
def package(request, category, package):
    package = get_object_or_404(Package, category=category, name=package)
    packaged = Version.objects.filter(package=package, packaged=True)
    upstream = Version.objects.filter(package=package, packaged=False)
    return { 'package' : package, 'packaged' : packaged, 'upstream' : upstream }
