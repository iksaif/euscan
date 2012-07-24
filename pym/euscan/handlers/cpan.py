import re
import portage
import urllib2
import json

from euscan import helpers, output

HANDLER_NAME = "cpan"
CONFIDENCE = 100.0
PRIORITY = 100

_cpan_package_name_re = re.compile("mirror://cpan/authors/.*/([^/.]*).*")


def can_handle(pkg, url):
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


def gentoo_mangle_version(up_pv):
    pv = ""

    if up_pv.count('.') == 1:
        digits = 0
        for i in range(len(up_pv)):
            if digits == 3:
                pv += "."
                digits = 0
            c = up_pv[i]
            pv += c
            digits += int(c.isdigit())
            if c == '.':
                digits = 0
    else:
        pv = up_pv

    return helpers.gentoo_mangle_version(pv)


def cpan_trim_version(pv):
    pv = re.sub('^[a-zA-Z]+', '', pv)
    pv = re.sub('[a-zA-Z]$', '', pv)
    return pv


def cpan_mangle_version(pv):
    pos = pv.find('.')
    if pos < 0:
        return pv
    up_pv = pv.replace('.', '')
    up_pv = up_pv[0:pos] + '.' + up_pv[pos:]
    up_pv = cpan_trim_version(up_pv)
    return up_pv


def cpan_vercmp(cp, a, b):
    try:
        return float(a) - float(b)
    except:
        if a < b:
            return -1
        else:
            return 1


def scan(pkg, url):
    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    pkg = guess_package(cp, url)

    orig_url = url
    url = 'http://search.cpan.org/api/dist/%s' % pkg

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
    data = json.loads(data)

    if 'releases' not in data:
        return []

    ret = []

    for version in data['releases']:
        #if version['status'] == 'testing':
        #    continue

        up_pv = version['version']
        up_pv = cpan_trim_version(up_pv)
        pv = gentoo_mangle_version(up_pv)
        up_ver = cpan_mangle_version(ver)

        if helpers.version_filtered(cp, up_ver, up_pv, cpan_vercmp):
            continue

        url = 'mirror://cpan/authors/id/%s/%s/%s/%s' % (
            version['cpanid'][0],
            version['cpanid'][0:1],
            version['cpanid'],
            version['archive']
        )

        if url == orig_url:
            continue

        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))

    return ret


def brute_force(pkg, url):
    return []
