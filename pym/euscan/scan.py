from __future__ import print_function

import os
import sys
from datetime import datetime

import portage
from portage.dbapi import porttree

import gentoolkit.pprinter as pp
from gentoolkit.query import Query
from gentoolkit.package import Package

from euscan import CONFIG, BLACKLIST_PACKAGES
from euscan import handlers, output
from euscan.helpers import version_blacklisted
from euscan.version import is_version_stable
from euscan.ebuild import package_from_ebuild


def filter_versions(cp, versions):
    filtered = {}

    for url, version, handler, confidence in versions:

        # Try to keep the most specific urls (determinted by the length)
        if version in filtered and len(url) < len(filtered[version]):
            continue

        # Remove blacklisted versions
        if version_blacklisted(cp, version):
            continue

        filtered[version] = {
            "url": url,
            "handler": handler,
            "confidence": confidence
        }

    return [
        (cp, filtered[version]["url"], version, filtered[version]["handler"],
         filtered[version]["confidence"])
        for version in filtered
    ]


# gentoolkit stores PORTDB, so even if we modify it to add an overlay
# it will still use the old dbapi
def reload_gentoolkit():
    from gentoolkit import dbapi
    import gentoolkit.package
    import gentoolkit.query

    PORTDB = portage.db[portage.root]["porttree"].dbapi
    dbapi.PORTDB = PORTDB

    if hasattr(dbapi, 'PORTDB'):
        dbapi.PORTDB = PORTDB
    if hasattr(gentoolkit.package, 'PORTDB'):
        gentoolkit.package.PORTDB = PORTDB
    if hasattr(gentoolkit.query, 'PORTDB'):
        gentoolkit.query.PORTDB = PORTDB


def scan_upstream(query, on_progress=None):
    """
    Scans the upstream searching new versions for the given query
    """
    matches = []

    if query.endswith(".ebuild"):
        cpv = package_from_ebuild(query)
        if cpv:
            reload_gentoolkit()
            matches = [Package(cpv)]
    else:
        matches = Query(query).find(
            include_masked=True,
            in_installed=False
        )

    if not matches:
        output.ewarn(
            pp.warn("No package matching '%s'" % pp.pkgquery(query))
        )
        return None

    matches = sorted(matches)
    pkg = matches.pop()

    while '9999' in pkg.version and len(matches):
        pkg = matches.pop()

    if not pkg:
        output.ewarn(
            pp.warn("Package '%s' only have a dev version (9999)"
                    % pp.pkgquery(pkg.cp))
        )
        return None

    # useful data only for formatted output
    start_time = datetime.now()
    output.metadata("datetime", start_time.isoformat(), show=False)
    output.metadata("cp", pkg.cp, show=False)
    output.metadata("cpv", pkg.cpv, show=False)

    if on_progress:
        on_progress(increment=10)

    if pkg.cp in BLACKLIST_PACKAGES:
        output.ewarn(
            pp.warn("Package '%s' is blacklisted" % pp.pkgquery(pkg.cp))
        )
        return None

    if not CONFIG['quiet']:
        if not CONFIG['format']:
            pp.uprint(
                " * %s [%s]" % (pp.cpv(pkg.cpv), pp.section(pkg.repo_name()))
            )
            pp.uprint()
        else:
            output.metadata("overlay", pp.section(pkg.repo_name()))

        ebuild_path = pkg.ebuild_path()
        if ebuild_path:
            output.metadata(
                "ebuild", pp.path(os.path.normpath(ebuild_path))
            )

        output.metadata("repository", pkg.repo_name())
        output.metadata("homepage", pkg.environment("HOMEPAGE"))
        output.metadata("description", pkg.environment("DESCRIPTION"))

    cpv = pkg.cpv
    metadata = {
        "EAPI": portage.settings["EAPI"],
        "SRC_URI": pkg.environment("SRC_URI", False),
    }
    use = frozenset(portage.settings["PORTAGE_USE"].split())
    try:
        alist = porttree._parse_uri_map(cpv, metadata, use=use)
        aalist = porttree._parse_uri_map(cpv, metadata)
    except Exception as e:
        output.ewarn(pp.warn("%s\n" % str(e)))
        output.ewarn(
            pp.warn("Invalid SRC_URI for '%s'" % pp.pkgquery(cpv))
        )
        return None

    if "mirror" in portage.settings.features:
        urls = aalist
    else:
        urls = alist

    versions = handlers.scan(pkg, urls, on_progress)

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    result = filter_versions(cp, versions)

    if on_progress:
        on_progress(increment=10)

    # output scan time for formatted output
    scan_time = (datetime.now() - start_time).total_seconds()
    output.metadata("scan_time", scan_time, show=False)

    is_current_version_stable = is_version_stable(ver)
    if len(result) > 0:
        if not (CONFIG['format'] or CONFIG['quiet']):
            print("\n", file=sys.stderr)

        for cp, url, version, handler, confidence in result:
            if CONFIG["ignore-pre-release"]:
                if not is_version_stable(version):
                    continue
            if CONFIG["ignore-pre-release-if-stable"]:
                if is_current_version_stable and \
                   not is_version_stable(version):
                    continue
            output.result(cp, version, url, handler, confidence)

    return result
