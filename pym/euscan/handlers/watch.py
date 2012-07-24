import re
import urllib2

import portage

from euscan.handlers import generic
from euscan import output, helpers

PRIORITY = 100

HANDLER_NAME = "watch"
CONFIDENCE = 100.0


is_pattern = r"\([^\/]+\)"


def can_handle(pkg, url):
    try:
        return pkg.metadata._xml_tree.find("upstream").find("watch") \
               is not None
    except AttributeError:
        return False


def parse_mangles(mangles, string):
    for mangle in mangles:
        # convert regex from perl format to python format
        m = re.match(r"s/(.*[^\\])/(.*)/", mangle)
        pattern, repl = m.groups()
        repl = re.sub(r"\$(\d+)", r"\\\1", repl)
        string = re.sub(pattern, repl, string)
    return string


def clean_results(results, versionmangle, urlmangle):
    ret = []

    for path, version, _, _ in results:
        version = parse_mangles(versionmangle, version)
        path = parse_mangles(urlmangle, path)
        ret.append((path, version, HANDLER_NAME, CONFIDENCE))

    return ret


def parse_watch(pkg):
    for watch_tag in pkg.metadata._xml_tree.find("upstream").findall("watch"):
        try:
            base, file_pattern = watch_tag.text.split(" ")[:2]
        except ValueError:
            base, file_pattern = watch_tag.text, None

        # the file pattern can be in the base url
        pattern_regex = r"/([^/]*\([^/]*\)[^/]*)$"
        match = re.search(pattern_regex, base)
        if match:
            file_pattern = match.group(1)
            base = base.replace(file_pattern, "")

        # handle sf.net specially
        base = base.replace(
            "http://sf.net/", "http://qa.debian.org/watch/sf.php/"
        )

        vmangle = watch_tag.attrib.get("uversionmangle", None) or \
                  watch_tag.attrib.get("versionmangle", None)
        versionmangle = vmangle.split(";") if vmangle else []

        umangle = watch_tag.attrib.get("downloadurlmangle", None)
        urlmangle = umangle.split(";") if umangle else []

        yield (base, file_pattern, versionmangle, urlmangle)


def handle_directory_patterns(base, file_pattern):
    """
    Directory pattern matching
    e.g.: base: ftp://ftp.nessus.org/pub/nessus/nessus-([\d\.]+)/src/
          file_pattern: nessus-core-([\d\.]+)\.tar\.gz
    """
    splitted = base.split("/")
    i = 0
    basedir = []
    for elem in splitted:
        if re.search(is_pattern, elem):
            break
        basedir.append(elem)
        i += 1
    basedir = "/".join(basedir)
    directory_pattern = splitted[i]
    final = "/".join(splitted[i + 1:])

    try:
        fp = helpers.urlopen(basedir)
    except urllib2.URLError:
        return []
    except IOError:
        return []

    if not fp:
        return []

    data = fp.read()

    if basedir.startswith("ftp://"):
        scan_data = generic.scan_ftp(data, basedir, directory_pattern)
    else:
        scan_data = generic.scan_html(data, basedir, directory_pattern)

    return [("/".join((basedir, path, final)), file_pattern)
            for _, path in scan_data]


def scan(pkg, url):
    output.einfo("Using watch data")

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    results = []
    for base, file_pattern, versionmangle, urlmangle in parse_watch(pkg):
        if not re.search(is_pattern, base):
            steps = [(base, file_pattern)]
            res = generic.scan_directory_recursive(
                cp, ver, rev, "", steps, url
            )
        else:
            res = []
            for step in handle_directory_patterns(base, file_pattern):
                res += generic.scan_directory_recursive(
                    cp, ver, rev, "", [step], url
                )

        results += clean_results(res, versionmangle, urlmangle)
    return results


def brute_force(pkg, url):
    return []
