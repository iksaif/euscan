import re
import portage
import urllib2
import xml.dom.minidom

from euscan import helpers, output

def can_handle(cpv, url):
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

def scan(cpv, url):
    pkg, channel = guess_package_and_channel(cpv, url)

    orig_url = url
    url = 'http://%s/rest/r/%s/allreleases.xml' % (channel, pkg.lower())

    output.einfo("Using: " + url)

    try:
        fp = helpers.urlopen(url)
    except urllib2.URLError:
        return []
    except IOError:
        return []

    data = fp.read()

    dom = xml.dom.minidom.parseString(data)

    nodes = dom.getElementsByTagName("v")
    ret = []

    cp, ver, rev = portage.pkgsplit(cpv)

    for node in nodes:
        version = node.childNodes[0].data
        if helpers.version_filtered(cp, ver, version):
            continue

        url = 'http://%s/get/%s-%s.tgz' % (channel, pkg, version)

        if url == orig_url:
            continue

        ret.append(( url, version ))

    return ret

def brute_force(cpv, url):
    return []
