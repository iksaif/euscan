import re
import portage
import json
import urllib2

from euscan import helpers, output, mangling

HANDLER_NAME = "rubygems"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url=None):
    return url and url.startswith('mirror://rubygems/')


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


def scan_url(pkg, url, options):
    'http://guides.rubygems.org/rubygems-org-api/#gemversion'

    gem = guess_gem(pkg.cpv, url)

    if not gem:
        output.eerror("Can't guess gem name using %s and %s" % \
            (pkg.cpv, url))
        return []

    output.einfo("Using RubyGem API: %s" % gem)

    return scan_pkg(pkg, {'data': gem})


def scan_pkg(pkg, options):
    gem = options['data']
    url = 'http://rubygems.org/api/v1/versions/%s.json' % gem

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

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    ret = []
    for version in versions:
        up_pv = version['number']
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        url = 'http://rubygems.org/gems/%s-%s.gem' % (gem, up_pv)
        url = mangling.mangle_url(url, options)
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
