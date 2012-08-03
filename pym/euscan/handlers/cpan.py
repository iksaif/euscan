import re
import portage
import urllib2
import json

from euscan import helpers, output, mangling

HANDLER_NAME = "cpan"
CONFIDENCE = 100
PRIORITY = 90

_cpan_package_name_re = re.compile("mirror://cpan/authors/.*/([^/.]*).*")

def can_handle(pkg, url=None):
    return url and url.startswith('mirror://cpan/')

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


def mangle_version(up_pv):
    # clean
    up_pv = up_pv.replace("._", "_")  # e.g.: 0.999._002 -> 0.999_002
    up_pv = up_pv.replace("_0.", "_")  # e.g.: 0.30_0.1 -> 0.30_1

    # Detect _rc versions
    rc_part = ""
    if up_pv.count("_") == 1:
        up_pv, rc_part = up_pv.split("_")

    # Gentoo creates groups of 3 digits, except for the first digit,
    # or when last digit is 0.  e.g.: 4.11 -> 4.110.0
    splitted = up_pv.split(".")
    if rc_part:
        splitted.append(rc_part)

    if len(splitted) == 2:  # add last group if it's missing
        splitted.append("0")

    groups = [splitted[0]]
    for part in splitted[1:-1]:
        groups.append(part.ljust(3, "0"))
    if splitted[-1] == "0":
        groups.append(splitted[-1])
    else:
        groups.append(splitted[-1].ljust(3, "0"))

    # if there's a group with leading zeros strip it.  e.g.: 002 -> 2
    groups = [g.lstrip("0") if g != "0" else g for g in groups]

    pv = ".".join(groups)

    if rc_part:
        pv = "%s_rc" % pv

    return pv

def scan_url(pkg, url, options):
    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    remote_pkg = guess_package(cp, url)

    output.einfo("Using CPAN API: %s", remote_pkg)

    return scan_pkg(pkg, {'data' : remote_pkg})

def scan_pkg(pkg, options):
    remote_pkg = options['data']

    # Defaults to CPAN mangling rules
    if 'versionmangle' not in options:
        options['versionmangle'] = ['cpan', 'gentoo']

    url = 'http://search.cpan.org/api/dist/%s' % remote_pkg
    cp, ver, rev = pkg.cp, pkg.version, pkg.revision

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
        pv = mangling.mangle_version(up_pv, options)

        if helpers.version_filtered(cp, ver, pv):
            continue

        url = 'mirror://cpan/authors/id/%s/%s/%s/%s' % (
            version['cpanid'][0],
            version['cpanid'][0:1],
            version['cpanid'],
            version['archive']
        )

        url = mangling.mangle_url(url, options)
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))

    return ret
