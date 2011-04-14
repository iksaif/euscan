from annoying.decorators import render_to
from django.http import Http404
from django.db.models import Sum, Max

from euscan.models import Version, Package, Herd, Maintainer, EuscanResult

@render_to('euscan/index.html')
def index(request):
    ctx = {}
    ctx['n_packaged'] = Package.objects.aggregate(Sum('n_packaged'))['n_packaged__sum']
    ctx['n_versions'] = Package.objects.aggregate(Sum('n_versions'))['n_versions__sum']
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
    return {}

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
    return {}
