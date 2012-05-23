import os
from datetime import datetime

import portage
from portage.dbapi import porttree

import gentoolkit.pprinter as pp
from gentoolkit.query import Query
from gentoolkit.eclean.search import (port_settings)

from euscan import CONFIG, BLACKLIST_PACKAGES
from euscan import handlers, helpers, output


def filter_versions(cp, versions):
    filtered = {}

    for url, version, handler, confidence in versions:

        # Try to keep the most specific urls (determinted by the length)
        if version in filtered and len(url) < len(filtered[version]):
            continue

        # Remove blacklisted versions
        if helpers.version_blacklisted(cp, version):
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


def scan_upstream_urls(cpv, urls):
    versions = []

    for filename in urls:
        for url in urls[filename]:
            if not CONFIG['quiet'] and not CONFIG['format']:
                pp.uprint()
            output.einfo("SRC_URI is '%s'" % url)

            if '://' not in url:
                output.einfo("Invalid url '%s'" % url)
                continue

            # Try normal scan
            if CONFIG["scan-dir"]:
                versions.extend(handlers.scan(cpv, url))

            if versions and CONFIG['oneshot']:
                break

            # Brute Force
            if CONFIG["brute-force"] > 0:
                versions.extend(handlers.brute_force(cpv, url))

            if versions and CONFIG['oneshot']:
                break

    cp, ver, rev = portage.pkgsplit(cpv)
    return filter_versions(cp, versions)


def scan_upstream(query):

    # check if the query is an ebuild file.
    # if it's a valid ebuild convert the filename in an euscan query
    ebuild_query = helpers.query_from_ebuild(query)
    if ebuild_query:
        query = ebuild_query

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
    output.metadata("datetime", datetime.now().isoformat(), show=False)
    output.metadata("cp", pkg.cp, show=False)
    output.metadata("cpv", pkg.cpv, show=False)

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
        "EAPI": port_settings["EAPI"],
        "SRC_URI": pkg.environment("SRC_URI", False),
    }
    use = frozenset(port_settings["PORTAGE_USE"].split())
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

    return scan_upstream_urls(pkg.cpv, urls)
