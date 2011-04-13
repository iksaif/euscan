from annoying.decorators import render_to
from django.http import Http404

@render_to('euscan/index.html')
def index(request):
    return {}

@render_to('euscan/logs.html')
def logs(request):
    return {}

@render_to('euscan/categories.html')
def categories(request):
    return {}

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
