# -*- coding: utf-8 -*-

import re
import urllib2

try:
    import simplejson as json
except ImportError:
    import json

import portage

from euscan import mangling, helpers, output

HANDLER_NAME = "gnome"
CONFIDENCE = 100
PRIORITY = 90

GNOME_URL_SOURCE = 'http://ftp.gnome.org/pub/GNOME/sources'

def can_handle(_pkg, url=None):
    return url and url.startswith('mirror://gnome/')


def guess_package(cp, url):
    match = re.search('mirror://gnome/sources/([^/]+)/.*', url)
    if match:
        return match.group(1)

    _cat, pkg = cp.split("/")

    return pkg


def scan_url(pkg, url, options):
    'http://ftp.gnome.org/pub/GNOME/sources/'
    package = guess_package(pkg.cpv, url)
    return scan_pkg(pkg, package)


def scan_pkg(pkg, options):
    # For some weird reasons package with no metadata 
    # will fail without this hack
    options = {
        'data': options,
        'type': 'gnome',
    }
    package = options['data']

    output.einfo("Using Gnome json cache: " + package)

    print 'Opening', '/'.join([GNOME_URL_SOURCE, package, 'cache.json'])
    fp = urllib2.urlopen('/'.join([GNOME_URL_SOURCE, package, 'cache.json']))
    content = fp.read()
    fp.close()

    cache = json.loads(content, encoding='ascii')

    if cache[0] != 4:
        raise Exception('Unknow cache format detected')

    versions = cache[2][package]

    if not versions:
        return versions

    versions.reverse()

    cp, ver, _rev = portage.pkgsplit(pkg.cpv)

    ret = []
    for up_pv in versions:
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        up_files = cache[1][package][up_pv]
        for tarball_comp in ('tar.xz', 'tar.bz2', 'tar.gz'):
            if tarball_comp in up_files:
                url = '/'.join([GNOME_URL_SOURCE, package,
                                 up_files[tarball_comp]])
                break
        else:
            raise Exception('No tarball for release ' + up_pv)
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
