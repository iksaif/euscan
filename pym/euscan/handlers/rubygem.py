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

    cp, ver, rev = portage.pkgsplit(cpv)
    cat, pkg = cp.split("/")

    return pkg

def scan(cpv, url):
    'http://guides.rubygems.org/rubygems-org-api/#gemversion'

    gem = guess_gem(cpv, url)
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
        version = version['number']
        if helpers.version_filtered(cp, ver, version):
            continue
        url = 'http://rubygems.org/gems/%s-%s.gem' % (gem, version)
        ret.append(( url, version ))

    return ret

def brute_force(cpv, url):
    return []
