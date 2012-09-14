import urllib
import re

import portage

from euscan import mangling, helpers, output

HANDLER_NAME = "deb"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url=None):
    return False


def scan_pkg(pkg, options):
    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    packages_url, package_name = options['data'].strip().split(" ", 1)

    output.einfo("Using Debian Packages: " + packages_url)

    fp = urllib.urlopen(packages_url)
    content = fp.read()

    # TODO: Add support for .gz and .bz2 Packages file

    content = content.split("\n\n")

    result = []

    for package_info in content:
        for line in package_info.split("\n"):
            res = re.search("^Version: (.*)$", line)
            if res:
                result.append(res.group(1))

    ret = []
    for up_pv in result:
        url = ""  # TODO: How to find the url?
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
