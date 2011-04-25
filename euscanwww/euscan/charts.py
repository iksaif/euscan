import os.path
import time

from euscanwww import settings

from django.db.models import F, Sum, Max
from euscan.models import Version, Package, Herd, Maintainer
from euscan.models import CategoryLog

import pylab
import matplotlib

CHARTS_ROOT = os.path.join(settings.MEDIA_ROOT, "charts")
CHARTS_URL = os.path.join(settings.MEDIA_URL, "charts")
CHARTS_TTL = (24 * 60 * 60)

pylab.rcParams['font.size'] = 10.0
pylab.rcParams['axes.titlesize'] = 10.0
pylab.rcParams['xtick.labelsize'] = 8.0
pylab.rcParams['legend.fontsize'] = 8.0

def xint(i):
    try:
        return int(i)
    except:
        return 0

def chart_alive(name):
    path = os.path.join(CHARTS_ROOT, name)
    if not os.path.exists(path):
        return False
    if os.path.getmtime(__file__) > os.path.getmtime(path):
        return False
    if os.path.getmtime(path) + CHARTS_TTL < time.time():
        return False
    return True

def chart_name(name, **kwargs):
    if 'category' in kwargs and kwargs['category']:
        name += '-%s' % kwargs['category']
    if 'herd' in kwargs and kwargs['herd']:
        name += '-h-%d' % kwargs['herd'].id
    if 'maintainer' in kwargs and kwargs['maintainer']:
        name += '-m-%d' % kwargs['maintainer'].id
    return name + ".png"

def packages(**kwargs):
    packages = Package.objects

    if 'category' in kwargs and kwargs['category']:
        packages = packages.filter(category=kwargs['category'])
    if 'herd' in kwargs and kwargs['herd']:
        packages = packages.filter(herds__id=kwargs['herd'].id)
    if 'maintainer' in kwargs and kwargs['maintainer']:
        packages = packages.filter(maintainers__id=kwargs['maintainer'].id)

    return packages

def cached_pylab_chart(f):
    def new_f(*args, **kwds):
        name = chart_name(f.func_name, **kwds)

        if not chart_alive(name):
            f(*args, **kwds)
            pylab.savefig(os.path.join(CHARTS_ROOT, name))
            pylab.close()

        return name

    new_f.func_name = f.func_name
    return new_f

@cached_pylab_chart
def pie_versions(**kwargs):
    n_packaged = xint(packages(**kwargs).aggregate(Sum('n_packaged'))['n_packaged__sum'])
    n_overlay = xint(packages(**kwargs).aggregate(Sum('n_overlay'))['n_overlay__sum'])
    n_versions = xint(packages(**kwargs).aggregate(Sum('n_versions'))['n_versions__sum'])
    n_upstream = n_versions - n_packaged - n_overlay

    pylab.figure(1, figsize=(3.5,3.5))

    if n_overlay:
        labels = 'Gentoo', 'Overlays', 'Upstream'
        fracs = [n_packaged, n_overlay, n_upstream]
        colors = '#008000', '#0B17FD', '#FF0000'
    else:
        labels = 'Gentoo', 'Upstream'
        fracs = [n_packaged, n_upstream]
        colors = '#008000', '#FF0000'

    pylab.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    pylab.title('Versions', bbox={'facecolor':'0.8', 'pad':5})

@cached_pylab_chart
def pie_packages(**kwargs):
    n_packages = packages(**kwargs).count()
    n_packages_uptodate_main = packages(**kwargs).filter(n_versions=F('n_packaged')).count()
    n_packages_uptodate_all = packages(**kwargs).filter(n_versions=F('n_packaged') + F('n_overlay')).count()
    n_packages_outdated = n_packages - n_packages_uptodate_all
    n_packages_uptodate_ovl = n_packages_uptodate_all - n_packages_uptodate_main

    pylab.figure(1, figsize=(3.5,3.5))

    if n_packages_uptodate_ovl:
        labels = 'Ok (gentoo)', 'Ok (overlays)', 'Outdated'
        fracs = [n_packages_uptodate_main, n_packages_uptodate_ovl, n_packages_outdated]
        colors = '#008000', '#0B17FD', '#FF0000'
    else:
        labels = 'Ok (gentoo)', 'Outdated'
        fracs = [n_packages_uptodate_main, n_packages_outdated]
        colors = '#008000', '#FF0000'

    pylab.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    pylab.title('Packages', bbox={'facecolor':'0.8', 'pad':5})

