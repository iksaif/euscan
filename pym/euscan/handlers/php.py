import re
import portage
import urllib2
import xml.dom.minidom

from euscan import helpers, output

HANDLER_NAME = "php"
CONFIDENCE = 100.0
PRIORITY = 90


def can_handle(pkg, url):
    if url.startswith('http://pear.php.net/get/'):
        return True
    if url.startswith('http://pecl.php.net/get/'):
        return True
    return False


def guess_package_and_channel(cp, url):
    match = re.search('http://(.*)/get/(.*)-(.*).tgz', url)

    if match:
        host = match.group(1)
        pkg = match.group(2)
    else:
        cat, pkg = cp.split("/")

    return pkg, host


def scan(pkg, url):
    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    package, channel = guess_package_and_channel(cp, url)

    orig_url = url
    url = 'http://%s/rest/r/%s/allreleases.xml' % (channel, package.lower())

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
        pv = helpers.gentoo_mangle_version(up_pv)
        if helpers.version_filtered(cp, ver, pv):
            continue

        url = 'http://%s/get/%s-%s.tgz' % (channel, package, up_pv)

        if url == orig_url:
            continue

        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))

    return ret


def brute_force(pkg, url):
    return []
