import urllib2
import re
import StringIO

from BeautifulSoup import BeautifulSoup

import portage

from euscan import CONFIG, SCANDIR_BLACKLIST_URLS, BRUTEFORCE_BLACKLIST_PACKAGES, BRUTEFORCE_BLACKLIST_URLS, output
from euscan import helpers

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

def scan_directory_recursive(cpv, url, steps):
    if not steps:
        return []

    cp, ver, rev = portage.pkgsplit(cpv)
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

    for version, path in results:
        if helpers.version_filtered(cp, ver, version):
            continue

        if not url.endswith('/') and not path.startswith('/'):
            path = url + '/' + path
        else:
            path = url + path

        versions.append((path, version))

        if steps:
            ret = scan_directory_recursive(cpv, path, steps)
            versions.extend(ret)

    return versions

def scan(cpv, url):
    for bu in SCANDIR_BLACKLIST_URLS:
        if re.match(bu, url):
            output.einfo("%s is blacklisted by rule %s" % (url, bu))
            return []

    resolved_url = helpers.parse_mirror(url)

    cp, ver, rev = portage.pkgsplit(cpv)

    template = helpers.template_from_url(resolved_url, ver)
    if '${' not in template:
        output.einfo("Url doesn't seems to depend on version: %s not found in %s"
                     % (ver, resolved_url))
        return []
    else:
        output.einfo("Scanning: %s" % template)

    steps = helpers.generate_scan_paths(template)
    return scan_directory_recursive(cpv, "", steps)

def brute_force(cpv, url):
    cp, ver, rev = portage.pkgsplit(cpv)

    url = helpers.parse_mirror(url)

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

    """ Remove unwanted versions """
    for v in versions:
        if helpers.vercmp(cp, ver, helpers.join_version(v)) >= 0:
            versions.remove(v)

    if not versions:
        output.einfo("Can't generate new versions from " + ver)
        return []

    template = helpers.template_from_url(url, ver)

    if '${PV}' not in template:
        output.einfo("Url doesn't seems to depend on full version: %s not found in %s"
                     % (ver, url))
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

        result.append([url, version])

        if len(result) > CONFIG['brute-force-false-watermark']:
            output.einfo("Broken server detected ! Skipping brute force.")
            return []

        if CONFIG["brute-force-recursive"]:
            for v in helpers.gen_versions(list(components), CONFIG["brute-force"]):
                if v not in versions and tuple(v) not in done:
                    versions.append(v)

        if CONFIG["oneshot"]:
            break

    return result

def can_handle(cpv, url):
    return True
