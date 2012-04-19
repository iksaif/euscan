import re
import portage
import json
import urllib2

from euscan import helpers
import euscan

def can_handle(cpv, url):
    return url.startswith('mirror://rubygems/')

def guess_gem(cpv, url):
    match = re.search('mirror://rubygems/(.*).gem', url)
    if match:
        cpv = 'fake/%s' % match.group(1)

    ret = portage.pkgsplit(cpv)
    if not ret:
        return None

    cp, ver, rev = ret
    cat, pkg = cp.split("/")

    return pkg

def scan(cpv, url):
    'http://guides.rubygems.org/rubygems-org-api/#gemversion'

    gem = guess_gem(cpv, url)
    if not gem:
        euscan.output.eerror("Can't guess gem name using %s and %s" % (cpv, url))
        return []

    url = 'http://rubygems.org/api/v1/versions/%s.json' % gem

    euscan.output.einfo("Using: " + url)

    try:
        fp = helpers.urlopen(url)
    except urllib2.URLError:
        return []
    except IOError:
        return []

    if not fp:
        return []

    data = fp.read()
    versions = json.loads(data)

    if not versions:
        return []

    cp, ver, rev = portage.pkgsplit(cpv)

    ret = []

    for version in versions:
        up_pv = version['number']
        pv = helpers.gentoo_mangle_version(up_pv)
        if helpers.version_filtered(cp, ver, pv):
            continue
        url = 'http://rubygems.org/gems/%s-%s.gem' % (gem, up_pv)
        ret.append(( url, pv ))

    return ret

def brute_force(cpv, url):
    return []
