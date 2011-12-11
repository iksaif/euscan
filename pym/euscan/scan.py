import os
import sys

import portage

from portage.dbapi import porttree
from portage.output import white, yellow, turquoise, green, teal, red, EOutput

import gentoolkit.pprinter as pp
from gentoolkit import errors
from gentoolkit.query import Query
from gentoolkit.eclean.search import (port_settings)

from euscan import CONFIG, BLACKLIST_PACKAGES
from euscan import handlers
from euscan import helpers

import euscan

def filter_versions(cp, versions):
    filtered = {}

    for url, version in versions:


        ''' Try to keep the most specific urls (determinted by the length) '''
        if version in filtered and len(url) < len(filtered[version]):
            continue

        ''' Remove blacklisted versions '''
        if helpers.version_blacklisted(cp, version):
            continue

        filtered[version] = url

    return [ (cp, filtered[version], version) for version in filtered ]

def scan_upstream_urls(cpv, urls):
    versions = []

    for filename in urls:
        for url in urls[filename]:
            if not CONFIG['quiet']:
                pp.uprint()
            euscan.output.einfo("SRC_URI is '%s'" % url)

            if '://' not in url:
                euscan.output.einfo("Invalid url '%s'" % url)
                continue

            ''' Try normal scan '''
            if CONFIG["scan-dir"]:
                versions.extend(handlers.scan(cpv, url))

            if versions and CONFIG['oneshot']:
                break

            ''' Brute Force '''
            if CONFIG["brute-force"] > 0:
                versions.extend(handlers.brute_force(cpv, url))

            if versions and CONFIG['oneshot']:
                break

    cp, ver, rev = portage.pkgsplit(cpv)
    return filter_versions(cp, versions)


def scan_upstream(query):
    matches = Query(query).find(
        include_masked=True,
        in_installed=False
    )

    if not matches:
        sys.stderr.write(pp.warn("No package matching '%s'" % pp.pkgquery(query)))
        return []

    matches = sorted(matches)
    pkg = matches.pop()

    while '9999' in pkg.version and len(matches):
        pkg = matches.pop()

    if not pkg:
        sys.stderr.write(pp.warn("Package '%s' only have a dev version (9999)"
                                 % pp.pkgquery(pkg.cp)))
        return []

    if pkg.cp in BLACKLIST_PACKAGES:
        sys.stderr.write(pp.warn("Package '%s' is blacklisted" % pp.pkgquery(pkg.cp)))
        return []

    if not CONFIG['quiet']:
        pp.uprint(" * %s [%s]" % (pp.cpv(pkg.cpv), pp.section(pkg.repo_name())))
        pp.uprint()

        ebuild_path = pkg.ebuild_path()
        if ebuild_path:
            pp.uprint('Ebuild: ' + pp.path(os.path.normpath(ebuild_path)))

        pp.uprint('Repository: ' + pkg.repo_name())
        pp.uprint('Homepage: ' + pkg.environment("HOMEPAGE"))
        pp.uprint('Description: ' + pkg.environment("DESCRIPTION"))

    cpv = pkg.cpv
    metadata = {
        "EAPI"    : port_settings["EAPI"],
        "SRC_URI" : pkg.environment("SRC_URI", False),
    }
    use = frozenset(port_settings["PORTAGE_USE"].split())
    try:
        alist = porttree._parse_uri_map(cpv, metadata, use=use)
        aalist = porttree._parse_uri_map(cpv, metadata)
    except Exception as e:
        sys.stderr.write(pp.warn("%s\n" % str(e)))
        sys.stderr.write(pp.warn("Invalid SRC_URI for '%s'" % pp.pkgquery(cpv)))
        return []

    if "mirror" in portage.settings.features:
        urls = aalist
    else:
        urls = alist

    return scan_upstream_urls(pkg.cpv, urls)
