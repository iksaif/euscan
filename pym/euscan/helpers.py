import os
import sys
import re
import pkg_resources
import errno
import imp

import urllib2

try:
    from urllib import robotparser
    from urllib import urlparse
except ImportError:
    import robotparser
    import urlparse

import portage
from portage import dep
from portage.const import VDB_PATH
from portage import _encodings
from portage import _shell_quote
from portage import _unicode_decode
from portage import _unicode_encode

from euscan import CONFIG, BLACKLIST_VERSIONS, ROBOTS_TXT_BLACKLIST_DOMAINS
import euscan


def htop_vercmp(a, b):
    def fixver(v):
        if v in ['0.11', '0.12', '0.13']:
            v = '0.1.' + v[3:]
        return v

    return simple_vercmp(fixver(a), fixver(b))

VERSION_CMP_PACKAGE_QUIRKS = {
    'sys-process/htop': htop_vercmp
}

_v_end = '((-|_)(pre|p|beta|b|alpha|a|rc|r)\d*)'
_v = r'((\d+)((\.\d+)*)([a-zA-Z]*?)(' + _v_end + '*))'


def get_version_type(version):
    types = []
    gentoo_types = ("alpha", "beta", "pre", "rc", "p")

    for token in re.findall("[\._-]([a-zA-Z]+)", version):
        if token in gentoo_types:
            types.append(token)
    if types:
        return types[0]
    return "release"


# Stolen from g-pypi
def gentoo_mangle_version(up_pv):
    """Convert PV to MY_PV if needed

    :param up_pv: Upstream package version
    :type up_pv: string
    :returns: pv
    :rtype: string

    Can't determine PV from upstream's version.
    Do our best with some well-known versioning schemes:

    * 1.0a1 (1.0_alpha1)
    * 1.0-a1 (1.0_alpha1)
    * 1.0b1 (1.0_beta1)
    * 1.0-b1 (1.0_beta1)
    * 1.0-r1234 (1.0_pre1234)
    * 1.0dev-r1234 (1.0_pre1234)
    * 1.0.dev-r1234 (1.0_pre1234)
    * 1.0dev-20091118 (1.0_pre20091118)

    Regex match.groups():
    * pkgfoo-1.0.dev-r1234
    * group 1 pv major (1.0)
    * group 2 replace this with portage suffix (.dev-r)
    * group 3 suffix version (1234)

    The order of the regexes is significant. For instance if you have
    .dev-r123, dev-r123 and -r123 you should order your regex's in
    that order.

    The chronological portage release versions are:

    * _alpha
    * _beta
    * _pre
    * _rc
    * release
    * _p

    **Example:**

    >>> gentoo_mangle_version('1.0b2')
        '1.0_beta2'

    .. note::
    The number of regex's could have been reduced, but we use four
    number of match.groups every time to simplify the code

    """
    bad_suffixes = re.compile(
        r'((?:[._-]*)(?:dev|devel|final|stable|snapshot)$)', re.I)
    revision_suffixes = re.compile(
        r'(.*?)([\._-]*(?:r|patch|p)[\._-]*)([0-9]*)$', re.I)
    suf_matches = {
        '_pre': [
            r'(.*?)([\._-]*dev[\._-]*r?)([0-9]+)$',
            r'(.*?)([\._-]*(?:pre|preview)[\._-]*)([0-9]*)$',
            ],
        '_alpha': [
            r'(.*?)([\._-]*(?:alpha|test)[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*a[\._-]*)([0-9]*)$',
            r'(.*[^a-z])(a)([0-9]*)$',
            ],
        '_beta': [
            r'(.*?)([\._-]*beta[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*b)([0-9]*)$',
            r'(.*[^a-z])(b)([0-9]*)$',
            ],
        '_rc': [
            r'(.*?)([\._-]*rc[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*c[\._-]*)([0-9]*)$',
            r'(.*[^a-z])(c[\._-]*)([0-9]+)$',
            ],
    }
    rs_match = None
    pv = up_pv
    additional_version = ""

    rev_match = revision_suffixes.search(up_pv)
    if rev_match:
        pv = up_pv = rev_match.group(1)
        replace_me = rev_match.group(2)
        rev = rev_match.group(3)
        additional_version = '_p' + rev

    for this_suf in suf_matches.keys():
        if rs_match:
            break
        for regex in suf_matches[this_suf]:
            rsuffix_regex = re.compile(regex, re.I)
            rs_match = rsuffix_regex.match(up_pv)
            if rs_match:
                portage_suffix = this_suf
                break

    if rs_match:
        # e.g. 1.0.dev-r1234
        major_ver = rs_match.group(1)  # 1.0
        replace_me = rs_match.group(2)  # .dev-r
        rev = rs_match.group(3)  # 1234
        pv = major_ver + portage_suffix + rev
    else:
        # Single suffixes with no numeric component are simply removed.
        match = bad_suffixes.search(up_pv)
        if match:
            suffix = match.groups()[0]
            pv = up_pv[: - (len(suffix))]

    pv = pv + additional_version

    return pv


def cast_int_components(version):
    for i, obj in enumerate(version):
        try:
            version[i] = int(obj)
        except ValueError:
            pass
    return version


def simple_vercmp(a, b):
    if a == b:
        return 0

    # For sane versions
    r = portage.versions.vercmp(a, b)

    if r is not None:
        return r

    # Fallback
    a = pkg_resources.parse_version(a)
    b = pkg_resources.parse_version(b)

    if a < b:
        return -1
    else:
        return 1


def vercmp(package, a, b):
    if package in VERSION_CMP_PACKAGE_QUIRKS:
        return VERSION_CMP_PACKAGE_QUIRKS[package](a, b)
    return simple_vercmp(a, b)


def version_is_nightly(a, b):
    a = pkg_resources.parse_version(a)
    b = pkg_resources.parse_version(b)

    ''' Try to skip nightly builds when not wanted (www-apps/moodle) '''
    if len(a) != len(b) and len(b) == 2 and len(b[0]) == len('yyyymmdd'):
        if b[0][:4] != '0000':
            return True
    return False


def version_blacklisted(cp, version):
    rule = None
    cpv = '%s-%s' % (cp, version)

    ''' Check that the generated cpv can be used by portage '''
    if not portage.versions.catpkgsplit(cpv):
        return False

    for bv in BLACKLIST_VERSIONS:
        if dep.match_from_list(bv, [cpv]):
            rule = bv
            None

    if rule:
        euscan.output.einfo("%s is blacklisted by rule %s" % (cpv, bv))
    return rule is not None


def version_change_end_sep(version):
    match = re.match('.*' + _v_end, version)
    if not match:
        return None
    end = match.group(1)
    if end[0] == '_':
        newend = end.replace('_', '-')
    elif end[0] == '-':
        newend = end.replace('-', '_')
    else:
        return None
    return version.replace(end, newend)


def version_filtered(cp, base, version, vercmp=vercmp):
    if vercmp(cp, base, version) >= 0:
        return True

    if version_blacklisted(cp, version):
        return True

    if version_is_nightly(base, version):
        return True

    return False


def generate_templates_vars(version):
    ret = []

    part = split_version(version)
    for i in range(2, len(part)):
        ver = []
        var = []
        for j in range(i):
            ver.append(str(part[j]))
            var.append('${%d}' % j)

        ret.append((".".join(ver), ".".join(var)))
    ret.append((version, '${PV}'))
    ret.reverse()
    return ret


def template_from_url(url, version):
    prefix, chunks = url.split('://')
    chunks = chunks.split('/')

    for i in range(len(chunks)):
        chunk = chunks[i]

        subs = generate_templates_vars(version)
        for sub in subs:
            chunk = chunk.replace(sub[0], sub[1])

        chunks[i] = chunk

    return prefix + "://" + "/".join(chunks)


def url_from_template(url, version):
    components = split_version(version)

    url = url.replace('${PV}', version)
    for i in range(len(components)):
        url = url.replace('${%d}' % i, str(components[i]))

    return url


# Stolen from distutils.LooseVersion
# Used for brute force to increment the version
def split_version(version):
    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)
    components = filter(lambda x: x and x != '.', component_re.split(version))
    for i in range(len(components)):
        try:
            components[i] = int(components[i])
        except ValueError:
            pass
    return components


def join_version(components):
    version = ""
    for i in range(len(components)):
        version += str(components[i])
        if i >= len(components) - 1:
            break
        if type(components[i]) != str and type(components[i + 1]) != str:
            version += "."
    return version


def increment_version(components, level):
    n = len(components)

    if level > n - 1 or level < 0:
        raise Exception

    for i in range(n, level + 1, -1):
        if type(components[i - 1]) == int:
            components[i - 1] = 0

    if type(components[level]) == int:
        components[level] += 1

    return components


def gen_versions(components, level):
    n = len(components)
    depth = level
    level = min(level, n)

    if not n:
        return []

    versions = []

    for i in range(n, n - level, -1):
        increment_version(components, i - 1)
        for j in range(depth):
            versions.append(list(components))
            increment_version(components, i - 1)

    return versions


def timeout_for_url(url):
    if 'sourceforge' in url:
        timeout = 15
    else:
        timeout = 5
    return timeout


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


""" RobotParser cache """
rpcache = {}


def urlallowed(url):
    if CONFIG['skip-robots-txt']:
        return True

    protocol, domain = urlparse.urlparse(url)[:2]

    for bd in ROBOTS_TXT_BLACKLIST_DOMAINS:
        if re.match(bd, domain):
            return True

    for d in ['sourceforge', 'berlios', 'github.com']:
        if d in domain:
            return True

    if protocol == 'ftp':
        return True

    baseurl = '%s://%s' % (protocol, domain)
    robotsurl = urlparse.urljoin(baseurl, 'robots.txt')

    if baseurl in rpcache:
        rp = rpcache[baseurl]
    else:
        from socket import setdefaulttimeout, getdefaulttimeout

        timeout = getdefaulttimeout()
        setdefaulttimeout(5)

        rp = robotparser.RobotFileParser()
        rp.set_url(robotsurl)
        try:
            rp.read()
            rpcache[baseurl] = rp
        except:
            rp = None

        setdefaulttimeout(timeout)

    return rp.can_fetch(CONFIG['user-agent'], url) if rp else False


def urlopen(url, timeout=None, verb="GET"):
    if not urlallowed(url):
        euscan.output.einfo("Url '%s' blocked by robots.txt" % url)
        return None

    if not timeout:
        timeout = timeout_for_url(url)

    if verb == 'GET':
        request = urllib2.Request(url)
    elif verb == 'HEAD':
        request = HeadRequest(url)
    else:
        return None

    request.add_header('User-Agent', CONFIG['user-agent'])

    handlers = []

    if CONFIG['cache']:
        from cache import CacheHandler
        handlers.append(CacheHandler(CONFIG['cache']))

    if CONFIG['verbose']:
        debuglevel = CONFIG['verbose'] - 1
        handlers.append(urllib2.HTTPHandler(debuglevel=debuglevel))

    opener = urllib2.build_opener(*handlers)

    return opener.open(request, None, timeout)


def tryurl(fileurl, template):
    result = True

    if not urlallowed(fileurl):
        euscan.output.einfo("Url '%s' blocked by robots.txt" % fileurl)
        return None

    euscan.output.ebegin("Trying: " + fileurl)

    try:
        basename = os.path.basename(fileurl)

        fp = urlopen(fileurl, verb='HEAD')
        if not fp:
            euscan.output.eend(errno.EPERM)
            return None

        headers = fp.info()

        if 'Content-disposition' in headers and \
           basename not in headers['Content-disposition']:
            result = None
        elif 'Content-Length' in headers and headers['Content-Length'] == '0':
            result = None
        elif 'Content-Type' in headers and \
             'text/html' in headers['Content-Type']:
            result = None
        elif 'Content-Type' in headers and \
             'application/x-httpd-php' in headers['Content-Type']:
            result = None
        elif fp.geturl() != fileurl:
            regex = regex_from_template(template)
            baseregex = regex_from_template(os.path.basename(template))
            basename2 = os.path.basename(fp.geturl())

            # Redirect to another (earlier?) version
            if basename != basename2 and (re.match(regex, fp.geturl()) or \
               re.match(baseregex, basename2)):
                result = None

            if result:
                result = (fp.geturl(), fp.info())

    except urllib2.URLError:
        result = None
    except IOError:
        result = None

    euscan.output.eend(errno.ENOENT if not result else 0)

    return result


def regex_from_template(template):
    # Escape
    template = re.escape(template)

    # Unescape specific stuff
    template = template.replace('\$\{', '${')
    template = template.replace('\}', '}')
    template = template.replace('}\.$', '}.$')

    # Replace ${\d+}
    #template = template.replace('${0}', r'([\d]+?)')
    template = re.sub(r'(\$\{\d+\}(\.?))+', r'([\w\.]+?)', template)

    #template = re.sub(r'(\$\{\d+\}\.?)+', r'([\w]+?)', template)
    #template = re.sub(r'(\$\{\d+\}\.+)+', '(.+?)\.', template)
    #template = re.sub(r'(\$\{\d+\})+', '(.+?)', template)

    # Full version
    template = template.replace('${PV}', _v)

    # End
    template = template + r'/?$'
    return template


def basedir_from_template(template):
    idx = template.find('${')
    if idx == -1:
        return template

    idx = template[0:idx].rfind('/')
    if idx == -1:
        return ""

    return template[0:idx]


def generate_scan_paths(url):
    prefix, chunks = url.split('://')
    chunks = chunks.split('/')

    steps = []

    path = prefix + ":/"
    for chunk in chunks:
        if '${' in chunk:
            steps.append((path, regex_from_template(chunk)))
            path = ""
        else:
            path += "/"
            path += chunk

    return steps


def parse_mirror(uri):
    from random import shuffle

    mirrors = portage.settings.thirdpartymirrors()

    if not uri.startswith("mirror://"):
        return uri

    eidx = uri.find("/", 9)
    if eidx == -1:
        euscan.output.einfo("Invalid mirror definition in SRC_URI:\n")
        euscan.output.einfo("  %s\n" % (uri))
        return None

    mirrorname = uri[9:eidx]
    path = uri[eidx + 1:]

    if mirrorname in mirrors:
        mirrors = mirrors[mirrorname]
        shuffle(mirrors)
        uri = mirrors[0].strip("/") + "/" + path
    else:
        euscan.output.einfo("No known mirror by the name: %s" % (mirrorname))
        return None

    return uri


# Stolen from ebuild
def query_from_ebuild(ebuild):
    pf = None
    if ebuild.endswith(".ebuild"):
        pf = os.path.basename(ebuild)[:-7]
    else:
        return False

    if not os.path.isabs(ebuild):
        mycwd = os.getcwd()
        # Try to get the non-canonical path from the PWD evironment variable,
        # since the canonical path returned from os.getcwd() may may be
        # unusable in cases where the directory stucture is built from
        # symlinks.
        pwd = os.environ.get('PWD', '')
        if sys.hexversion < 0x3000000:
            pwd = _unicode_decode(pwd, encoding=_encodings['content'],
                                  errors='strict')
        if pwd and pwd != mycwd and \
            os.path.realpath(pwd) == mycwd:
            mycwd = portage.normalize_path(pwd)
        ebuild = os.path.join(mycwd, ebuild)

    ebuild = portage.normalize_path(ebuild)
    # portdbapi uses the canonical path for the base of the portage tree, but
    # subdirectories of the base can be built from symlinks (like crossdev
    # does).
    ebuild_portdir = os.path.realpath(
      os.path.dirname(os.path.dirname(os.path.dirname(ebuild))))
    ebuild = os.path.join(ebuild_portdir, *ebuild.split(os.path.sep)[-3:])
    vdb_path = os.path.join(portage.settings['ROOT'], VDB_PATH)

    # Make sure that portdb.findname() returns the correct ebuild.
    if ebuild_portdir != vdb_path and \
        ebuild_portdir not in portage.portdb.porttrees:
        if sys.hexversion >= 0x3000000:
            os.environ["PORTDIR_OVERLAY"] = \
                os.environ.get("PORTDIR_OVERLAY", "") + \
                " " + _shell_quote(ebuild_portdir)
        else:
            os.environ["PORTDIR_OVERLAY"] = \
                os.environ.get("PORTDIR_OVERLAY", "") + \
                " " + _unicode_encode(_shell_quote(ebuild_portdir),
                encoding=_encodings['content'], errors='strict')

        portage.close_portdbapi_caches()
        imp.reload(portage)
    del portage.portdb.porttrees[1:]
    if ebuild_portdir != portage.portdb.porttree_root:
        portage.portdb.porttrees.append(ebuild_portdir)

    if not os.path.exists(ebuild):
        return False

    ebuild_split = ebuild.split("/")
    cpv = "%s/%s" % (ebuild_split[-3], pf)

    if not portage.catpkgsplit(cpv):
        return False

    if ebuild.startswith(os.path.join(portage.root, portage.const.VDB_PATH)):
        mytree = "vartree"

        portage_ebuild = portage.db[portage.root][mytree].dbapi.findname(cpv)

        if os.path.realpath(portage_ebuild) != ebuild:
            return False

    else:
        mytree = "porttree"

        portage_ebuild = portage.portdb.findname(cpv)

        if not portage_ebuild or portage_ebuild != ebuild:
            return False

    return cpv
