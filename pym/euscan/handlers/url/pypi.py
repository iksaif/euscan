import xmlrpclib
import re

import portage

from euscan import helpers, output

HANDLER_NAME = "pypi"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url):
    return url.startswith('mirror://pypi/')


def guess_package(cp, url):
    match = re.search('mirror://pypi/\w+/(.*)/.*', url)
    if match:
        return match.group(1)

    cat, pkg = cp.split("/")

    return pkg


def scan(pkg, url):
    'http://wiki.python.org/moin/PyPiXmlRpc'

    package = guess_package(pkg.cpv, url)

    ret = []
    for urls, pv in scan_remote(pkg, [package]):
        ret.append((urls, pv, HANDLER_NAME, CONFIDENCE))
    return ret


def scan_remote(pkg, remote_data):
    package = remote_data[0]

    output.einfo("Using PyPi XMLRPC: " + package)

    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    versions = client.package_releases(package)

    if not versions:
        return versions

    versions.reverse()

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    ret = []
    for up_pv in versions:
        pv = helpers.gentoo_mangle_version(up_pv)
        if helpers.version_filtered(cp, ver, pv):
            continue
        urls = client.release_urls(package, up_pv)
        urls = " ".join([infos['url'] for infos in urls])
        ret.append((urls, pv))
    return ret
