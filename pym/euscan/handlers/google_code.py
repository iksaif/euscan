import re
import portage

from euscan import output
from euscan.helpers import regex_from_template
from euscan.handlers.url import process_scan as url_scan

HANDLER_NAME = "google-code"
CONFIDENCE = 90
PRIORITY = 90


package_name_regex = r"http://(.+).googlecode.com/files/.+"


def can_handle(pkg, url=None):
    if not url:
        return False

    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    if ver not in url:
        return False

    return re.match(package_name_regex, url)

def scan_url(pkg, url, options):
    output.einfo("Using Google Code handler")

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    package_name = re.match(package_name_regex, url).group(1)
    base_url = "http://code.google.com/p/%s/downloads/list" % package_name

    file_pattern = regex_from_template(
        url.split("/")[-1].replace(ver, "${PV}")
    )

    result = url_scan(pkg, base_url, file_pattern)

    ret = []
    for url, pv, _, _ in result:
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
