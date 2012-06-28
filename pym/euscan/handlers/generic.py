import urllib2
import re
import StringIO

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import portage

from euscan import CONFIG, SCANDIR_BLACKLIST_URLS, \
    BRUTEFORCE_BLACKLIST_PACKAGES, BRUTEFORCE_BLACKLIST_URLS, output, helpers

HANDLER_NAME = "generic"
CONFIDENCE = 50.0
PRIORITY = 0

BRUTEFORCE_HANDLER_NAME = "brute_force"
BRUTEFORCE_CONFIDENCE = 30.0


def scan_html(data, url, pattern):
    soup = BeautifulSoup(data)
    results = []

    for link in soup.findAll('a'):
        href = link.get("href")
        if not href:
            continue

        if href.startswith(url):
            href = href.replace(url, "", 1)

        match = re.match(pattern, href, re.I)
        if match:
            results.append((match.group(1), match.group(0)))

    return results


def scan_ftp(data, url, pattern):
    buf = StringIO.StringIO(data)
    results = []

    for line in buf.readlines():
        line = line.replace("\n", "").replace("\r", "")
        match = re.search(pattern, line, re.I)
        if match:
            results.append((match.group(1), match.group(0)))

    return results


def scan_directory_recursive(cp, ver, rev, url, steps, orig_url):
    if not steps:
        return []

    url += steps[0][0]
    pattern = steps[0][1]

    steps = steps[1:]

    output.einfo("Scanning: %s" % url)

    try:
        fp = helpers.urlopen(url)
    except urllib2.URLError:
        return []
    except IOError:
        return []

    if not fp:
        return []

    data = fp.read()

    results = []

    if re.search("<\s*a\s+[^>]*href", data):
        results.extend(scan_html(data, url, pattern))
    elif url.startswith('ftp://'):
        results.extend(scan_ftp(data, url, pattern))

    versions = []

    for up_pv, path in results:
        pv = helpers.gentoo_mangle_version(up_pv)
        if helpers.version_filtered(cp, ver, pv):
            continue

        if not url.endswith('/') and not path.startswith('/'):
            path = url + '/' + path
        else:
            path = url + path

        if not steps and path not in orig_url:
            versions.append((path, pv, HANDLER_NAME, CONFIDENCE))

        if steps:
            ret = scan_directory_recursive(cp, ver, rev, path, steps, orig_url)
            versions.extend(ret)

    return versions


def scan(cpv, url):
    for bu in SCANDIR_BLACKLIST_URLS:
        if re.match(bu, url):
            output.einfo("%s is blacklisted by rule %s" % (url, bu))
            return []

    resolved_url = helpers.parse_mirror(url)
    if not resolved_url:
        return []

    cp, ver, rev = portage.pkgsplit(cpv)

    # 'Hack' for _beta/_rc versions where _ is used instead of -
    if ver not in resolved_url:
        newver = helpers.version_change_end_sep(ver)
        if newver and newver in resolved_url:
            output.einfo(
                "Version: using %s instead of %s" % (newver, ver)
            )
            ver = newver

    template = helpers.template_from_url(resolved_url, ver)
    if '${' not in template:
        output.einfo(
            "Url doesn't seems to depend on version: %s not found in %s" %
            (ver, resolved_url)
        )
        return []
    else:
        output.einfo("Scanning: %s" % template)

    steps = helpers.generate_scan_paths(template)
    ret = scan_directory_recursive(cp, ver, rev, "", steps, url)

    return ret


def brute_force(cpv, url):
    cp, ver, rev = portage.pkgsplit(cpv)

    url = helpers.parse_mirror(url)
    if not url:
        return []

    for bp in BRUTEFORCE_BLACKLIST_PACKAGES:
        if re.match(bp, cp):
            output.einfo("%s is blacklisted by rule %s" % (cp, bp))
            return []

    for bp in BRUTEFORCE_BLACKLIST_URLS:
        if re.match(bp, url):
            output.einfo("%s is blacklisted by rule %s" % (cp, bp))
            return []

    output.einfo("Generating version from " + ver)

    components = helpers.split_version(ver)
    versions = helpers.gen_versions(components, CONFIG["brute-force"])

    # Remove unwanted versions
    for v in versions:
        if helpers.vercmp(cp, ver, helpers.join_version(v)) >= 0:
            versions.remove(v)

    if not versions:
        output.einfo("Can't generate new versions from " + ver)
        return []

    template = helpers.template_from_url(url, ver)

    if '${PV}' not in template:
        output.einfo(
            "Url doesn't seems to depend on full version: %s not found in %s" %
            (ver, url))
        return []
    else:
        output.einfo("Brute forcing: %s" % template)

    result = []

    i = 0
    done = []

    while i < len(versions):
        components = versions[i]
        i += 1
        if components in done:
            continue
        done.append(tuple(components))

        version = helpers.join_version(components)

        if helpers.version_filtered(cp, ver, version):
            continue

        url = helpers.url_from_template(template, version)
        infos = helpers.tryurl(url, template)

        if not infos:
            continue

        result.append([url, version, BRUTEFORCE_HANDLER_NAME,
                       BRUTEFORCE_CONFIDENCE])

        if len(result) > CONFIG['brute-force-false-watermark']:
            output.einfo(
                "Broken server detected ! Skipping brute force."
            )
            return []

        if CONFIG["brute-force-recursive"]:
            for v in helpers.gen_versions(list(components),
                                          CONFIG["brute-force"]):
                if v not in versions and tuple(v) not in done:
                    versions.append(v)

        if CONFIG["oneshot"]:
            break

    return result


def can_handle(cpv, url):
    return True
