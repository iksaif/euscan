import re

import portage

from euscan.helpers import regex_from_template
from euscan.handlers.url import process_scan as url_scan
from euscan import output

HANDLER_NAME = "sourceforge"
CONFIDENCE = 90
PRIORITY = 90


def can_handle(pkg, url=None):
    if not url:
        return False

    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    if ver not in url:
        return False

    return "mirror://sourceforge/" in url


def scan_url(pkg, url, options):
    output.einfo("Using SourceForge handler")

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    project, filename = re.search(
        "mirror://sourceforge/([^/]+)/(?:.*/)?([^/]+)",
        url
    ).groups()

    base_url = "http://qa.debian.org/watch/sf.php/%s" % project
    file_pattern = regex_from_template(
        filename.replace(ver, "${PV}")
    )

    result = url_scan(pkg, base_url, file_pattern)

    ret = []
    for url, pv, _, _ in result:
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
