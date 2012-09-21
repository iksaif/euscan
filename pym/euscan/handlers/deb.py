import urllib
import re
import bz2
import zlib

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

    # Support for .gz and .bz2 Packages file
    if packages_url.endswith(".bz2"):
        content = bz2.decompress(content)
    if packages_url.endswith(".gz"):
        content = zlib.decompress(content, 16 + zlib.MAX_WBITS)

    content = content.split("\n\n")

    result = []

    for package_info in content:
        package_line = re.search(r"^Package: (.*)$", package_info, re.M)
        version_line = re.search(r"^Version: (.*)$", package_info, re.M)
        if package_line and package_line.group(1) == package_name:
            if version_line:
                result.append(version_line.group(1))

    ret = []
    for up_pv in result:
        url = ""  # TODO: How to find the url?
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
