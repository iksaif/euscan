import re
import portage
import urllib2
import xml.dom.minidom

from euscan import helpers, output, mangling

HANDLER_NAME = "php"
CONFIDENCE = 100
PRIORITY = 90

def can_handle(pkg, url=None):
    return False

def guess_package_and_channel(cp, url):
    match = re.search('http://(.*)\.php\.net/get/(.*)-(.*).tgz', url)

    if match:
        host = match.group(1)
        pkg = match.group(2)
    else:
        cat, pkg = cp.split("/")

    return pkg, host


def scan_url(pkg, url, options):
    package, channel = guess_package_and_channel(pkg.cp, url)
    return scan_pkg(pkg, {'type' : channel, 'data' : package })

def scan_pkg(pkg, options):
    cp, ver, rev = pkg.cp, pkg.version, pkg.revision

    package = options['data']
    channel = options['type']

    url = 'http://%s.php.net/rest/r/%s/allreleases.xml' % (channel, package.lower())

    output.einfo("Using: " + url)

    try:
        fp = helpers.urlopen(url)
    except urllib2.URLError:
        return []
    except IOError:
        return []

    if not fp:
        return []

    data = fp.read()

    dom = xml.dom.minidom.parseString(data)

    nodes = dom.getElementsByTagName("v")
    ret = []

    for node in nodes:
        up_pv = node.childNodes[0].data
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue

        url = 'http://%s.php.net/get/%s-%s.tgz' % (channel, package, up_pv)
        url = mangling.mangle_url(url, options)

        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))

    return ret
