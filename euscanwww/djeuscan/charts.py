import os.path
import time

from euscanwww import settings

from django.db.models import F, Sum
from djeuscan.models import Package

import rrdtool

import pylab

CHARTS_ROOT = os.path.join(settings.EUSCAN_ROOT, 'var', 'charts')
CHARTS_URL = os.path.join(settings.EUSCAN_ROOT, 'var', 'charts')
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


def rrd_name(**kwargs):
    name = ""

    if 'category' in kwargs and kwargs['category']:
        name = 'category-%s' % kwargs['category']
    elif 'herd' in kwargs and kwargs['herd']:
        name = 'herd-%d' % kwargs['herd'].id
    elif 'maintainer' in kwargs and kwargs['maintainer']:
        name = 'maintainer-%d' % kwargs['maintainer'].id
    else:
        name = 'world'

    return name


def chart_name(name, **kwargs):
    name = name.replace('_', '-')

    if 'category' in kwargs and kwargs['category']:
        name += '-%s' % kwargs['category']
    if 'herd' in kwargs and kwargs['herd']:
        name += '-h-%d' % kwargs['herd'].id
    if 'maintainer' in kwargs and kwargs['maintainer']:
        name += '-m-%d' % kwargs['maintainer'].id

    for kw in ('-small', '-weekly', '-monthly', '-yearly'):
        if kw in kwargs:
            name += kw

    return name + ".png"


def getpackages(**kwargs):
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
    gpk = getpackages(**kwargs)
    n_packaged = xint(gpk.aggregate(Sum('n_packaged'))['n_packaged__sum'])
    n_overlay = xint(gpk.aggregate(Sum('n_overlay'))['n_overlay__sum'])
    n_versions = xint(gpk.aggregate(Sum('n_versions'))['n_versions__sum'])
    n_upstream = n_versions - n_packaged - n_overlay

    pylab.figure(1, figsize=(3.5, 3.5))

    if n_overlay:
        labels = 'Gentoo', 'Overlays', 'Upstream'
        fracs = [n_packaged, n_overlay, n_upstream]
        colors = '#008000', '#0B17FD', '#FF0000'
    else:
        labels = 'Gentoo', 'Upstream'
        fracs = [n_packaged, n_upstream]
        colors = '#008000', '#FF0000'

    pylab.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%',
              shadow=True)
    pylab.title('Versions', bbox={'facecolor': '0.8', 'pad': 5})


@cached_pylab_chart
def pie_packages(**kwargs):
    gpk = getpackages(**kwargs)
    n_packages = gpk.count()
    n_packages_uptodate_main = gpk.filter(n_versions=F('n_packaged')).count()
    n_packages_uptodate_all = gpk.filter(n_versions=F('n_packaged') + \
                              F('n_overlay')).count()
    n_packages_outdated = n_packages - n_packages_uptodate_all
    n_packages_uptodate_ovl = n_packages_uptodate_all - \
                              n_packages_uptodate_main

    pylab.figure(1, figsize=(3.5, 3.5))

    if n_packages_uptodate_ovl:
        labels = 'Ok (gentoo)', 'Ok (overlays)', 'Outdated'
        fracs = [n_packages_uptodate_main, n_packages_uptodate_ovl,
                 n_packages_outdated]
        colors = '#008000', '#0B17FD', '#FF0000'
    else:
        labels = 'Ok (gentoo)', 'Outdated'
        fracs = [n_packages_uptodate_main, n_packages_outdated]
        colors = '#008000', '#FF0000'

    pylab.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%',
              shadow=True)
    pylab.title('Packages', bbox={'facecolor': '0.8', 'pad': 5})


def rrd_path(name):
    return str(os.path.join(settings.RRD_ROOT, name + '.rrd'))


def rrd_create(name, start):
    path = rrd_path(name)
    if os.path.exists(path):
        return
    rrdtool.create(path, '--step', '86400',
                   '--start', '%s' % int(start - 10),
                   'DS:n_packages_gentoo:GAUGE:4294967295:0:U',
                   'DS:n_packages_overlay:GAUGE:4294967295:0:U',
                   'DS:n_packages_outdated:GAUGE:4294967295:0:U',
                   'DS:n_versions_gentoo:GAUGE:4294967295:0:U',
                   'DS:n_versions_overlay:GAUGE:4294967295:0:U',
                   'DS:n_versions_upstream:GAUGE:4294967295:0:U',
                   'RRA:AVERAGE:0.5:1:100',
                   'RRA:AVERAGE:0.5:5:200',
                   'RRA:AVERAGE:0.5:10:200')


def rrd_update(name, datetime, values):
    now = time.mktime(datetime.timetuple())
    rrd_create(name, now)
    rrdtool.update(
        rrd_path(name),
        '%d:%d:%d:%d:%d:%d:%d' % \
            (now, values.n_packages_gentoo, values.n_packages_overlay,
             values.n_packages_outdated, values.n_versions_gentoo,
             values.n_versions_overlay, values.n_versions_upstream)
    )


"""
[-s|--start time] [-e|--end time] [-S|--step seconds]
[-t|--title string] [-v|--vertical-label string]
[-w|--width pixels] [-h|--height pixels] [-j|--only-graph] [-D|--full-size-mode][-u|--upper-limit value] [-l|--lower-limit value]
[-u|--upper-limit value] [-l|--lower-limit value] [-r|--rigid]
[-A|--alt-autoscale]
[-M|--alt-autoscale-max]
[-J|--alt-autoscale-min]
"""


def cached_rrd_chart(f):
    def new_f(*args, **kwds):
        if 'period' not in kwds:
            kwds['period'] = '-yearly'

        name = chart_name(f.func_name, **kwds)
        path = os.path.join(CHARTS_ROOT, name)

        if not chart_alive(name):
            kwds['title'] = '%s (%s)' % (f.func_name, kwds['period'])
            kwds['steps'] = kwds['period']
            kwds['vertical-label'] = f.func_name
            kwds['rrd'] = rrd_path(rrd_name(**kwds))
            kwds['path'] = path

            kwds['end'] = 'now'

            if kwds['period'] == '-weekly':
                kwds['start'] = 'now-4weeks'
            elif kwds['period'] == '-monthly':
                kwds['start'] = 'now-12months'
            else:
                kwds['start'] = 'now-4years'

            if '-small' in kwds and kwds['-small']:
                kwds['width'] = '100'
                kwds['height'] = '30'
                kwds['graph-mode'] = '--only-graph'
            else:
                kwds['width'] = '500'
                kwds['height'] = '170'
                kwds['graph-mode'] = '--full-size-mode'

            f(*args, **kwds)

        return name

    new_f.func_name = f.func_name
    return new_f


@cached_rrd_chart
def packages(**kwargs):
    rrdtool.graph(
        str(kwargs['path']),
        '--imgformat', 'PNG',
        '--width', kwargs['width'],
        '--height', kwargs['height'],
        kwargs['graph-mode'],
        '--color', 'CANVAS#FFFFFF00',
        '--color', 'BACK#FFFFFF00',

        '--start', kwargs['start'],
        '--end', kwargs['end'],
        '--vertical-label', kwargs['vertical-label'],
        '--title', kwargs['title'],
        '--lower-limit', '0',
        'DEF:n_packages_gentoo=%s:n_packages_gentoo:AVERAGE' % (kwargs['rrd']),
        'DEF:n_packages_overlay=%s:n_packages_overlay:AVERAGE' % \
            (kwargs['rrd']),
        'DEF:n_packages_outdated=%s:n_packages_outdated:AVERAGE' % \
            (kwargs['rrd']),
        'LINE1.25:n_packages_gentoo#008000:Gentoo',
        'LINE1.25:n_packages_overlay#0B17FD:Overlay',
        'LINE1.25:n_packages_outdated#FF0000:Outdated'
    )


@cached_rrd_chart
def versions(**kwargs):
    rrdtool.graph(
        str(kwargs['path']),
        '--imgformat', 'PNG',
        '--width', kwargs['width'],
        '--height', kwargs['height'],
        kwargs['graph-mode'],
        '--color', 'CANVAS#FFFFFF00',
        '--color', 'BACK#FFFFFF00',
        '--start', kwargs['start'],
        '--end', kwargs['end'],
        '--vertical-label', kwargs['vertical-label'],
        '--title', kwargs['title'],
        '--lower-limit', '0',
        'DEF:n_versions_gentoo=%s:n_versions_gentoo:AVERAGE' % (kwargs['rrd']),
        'DEF:n_versions_overlay=%s:n_versions_overlay:AVERAGE' % \
            (kwargs['rrd']),
        'DEF:n_versions_outdated=%s:n_versions_upstream:AVERAGE' % \
            (kwargs['rrd']),
        'LINE1.25:n_versions_gentoo#008000:Gentoo',
        'LINE1.25:n_versions_overlay#0B17FD:Overlay',
        'LINE1.25:n_versions_outdated#FF0000:Outdated'
    )
