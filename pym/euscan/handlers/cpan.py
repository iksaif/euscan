import re
import portage
import urllib2
import json

from euscan import helpers
import euscan

_cpan_package_name_re = re.compile("mirror://cpan/authors/.*/([^/.]*).*")

def can_handle(cpv, url):
    return url.startswith('mirror://cpan/')

def guess_package(cp, url):
    match = _cpan_package_name_re.search(url)

    pkg = None

    if match:
        pkg = match.group(1)
        try:
            cp, ver, rev = portage.pkgsplit('fake/' + pkg)
        except:
            pass

    cat, pkg = cp.split("/")

    return pkg

def scan(cpv, url):
    cp, ver, rev = portage.pkgsplit(cpv)
    pkg = guess_package(cp, url)

    orig_url = url
    url = 'http://search.cpan.org/api/dist/%s' % pkg

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
    data = json.loads(data)

    if 'releases' not in data:
        return []

    ret = []

    for version in data['releases']:
        up_pv = version['version']
        pv = helpers.gentoo_mangle_version(up_pv)

        if helpers.version_filtered(cp, ver, pv):
            continue

        url = 'mirror://cpan/authors/id/%s/%s/%s/%s' % \
            (version['cpanid'][0], version['cpanid'][0:1], version['cpanid'], version['archive'])

        if url == orig_url:
            continue

        ret.append(( url, pv ))

    return ret

def brute_force(cpv, url):
    return []
