import os
import re
import pkg_resources
import errno

import urllib2

try:
    from urllib import robotparser
    from urllib import urlparse
except ImportError:
    import robotparser
    import urlparse

import portage
from portage import dep

from euscan import CONFIG, BLACKLIST_VERSIONS, output

def htop_vercmp(a, b):
    def fixver(v):
        if v in ['0.11', '0.12', '0.13']:
            v = '0.1.' + v[3:]
        return v

    return simple_vercmp(fixver(a), fixver(b))

VERSION_CMP_PACKAGE_QUIRKS = {
    'sys-process/htop' : htop_vercmp
}

_v = r'((\d+)((\.\d+)*)([a-zA-Z]*?)(((-|_)(pre|p|beta|b|alpha|a|rc|r)\d*)*))'

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
        output.einfo("%s is blacklisted by rule %s" % (cpv, bv))
    return rule is not None

def version_filtered(cp, base, version):
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

    baseurl = '%s://%s' % (protocol, domain)
    robotsurl = urlparse.urljoin(baseurl, 'robots.txt')

    if rpcache.has_key(baseurl):
        rp = rpcache[baseurl]
    else:
        rp = robotparser.RobotFileParser()
        rp.set_url(robotsurl)
        rp.read()
        rpcache[baseurl] = rp
    return rp.can_fetch(CONFIG['user-agent'], url)

def urlopen(url, timeout=None, verb="GET"):
    if not urlallowed(url):
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
    return urllib2.urlopen(request, None, timeout)

def tryurl(fileurl, template):
    result = True

    if not urlallowed(fileurl):
        output.eerror("Url '%s' blocked by robots.txt" % fileurl)
        return None

    output.ebegin("Trying: " + fileurl)

    try:
        basename = os.path.basename(fileurl)

        fp = urlopen(fileurl, verb='HEAD')
        if not fp:
            output.eend(errno.EPERM)
            return None

        headers = fp.info()

        if 'Content-disposition' in headers and basename not in headers['Content-disposition']:
            result = None
        elif 'Content-Length' in headers and headers['Content-Length'] == '0':
            result = None
        elif 'Content-Type' in headers and 'text/html' in headers['Content-Type']:
            result = None
        elif fp.geturl() != fileurl:
            regex = regex_from_template(template)
            baseregex = regex_from_template(os.path.basename(template))
            basename2 = os.path.basename(fp.geturl())

            # Redirect to another (earlier?) version
            if basename != basename2 and (re.match(regex, fp.geturl()) or re.match(baseregex, basename2)):
                result = None


            if result:
                result = (fp.geturl(), fp.info())

    except urllib2.URLError:
        result = None
    except IOError:
        result = None

    output.eend(errno.ENOENT if not result else 0)

    return result

def regex_from_template(template):
    template = re.escape(template)
    template = template.replace('\$\{', '${')
    template = template.replace('\}', '}')
    template = template.replace('}\.$', '}.$')
    template = template.replace('${1}', r'([\d]+?)')
    template = re.sub(r'(\$\{\d+\}\.?)+', r'([\w]+?)', template)
    #template = re.sub(r'(\$\{\d+\}\.?)+', r'([\w]+?)', template)
    #template = re.sub(r'(\$\{\d+\}\.+)+', '(.+?)\.', template)
    #template = re.sub(r'(\$\{\d+\})+', '(.+?)', template)
    template = template.replace('${PV}', _v)
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
        output.einfo("Invalid mirror definition in SRC_URI:\n")
        output.einfo("  %s\n" % (uri))
        return None

    mirrorname = uri[9:eidx]
    path = uri[eidx+1:]

    if mirrorname in mirrors:
        mirrors = mirrors[mirrorname]
        shuffle(mirrors)
        uri = mirrors[0].strip("/") + "/" + path
    else:
        output.einfo("No known mirror by the name: %s\n" % (mirrorname))
        return None

    return uri
