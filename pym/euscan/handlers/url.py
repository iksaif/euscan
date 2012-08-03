import re
import urllib2

import portage

import generic
from euscan import output, helpers

PRIORITY = 100

HANDLER_NAME = "url"
CONFIDENCE = 100.0


is_pattern = r"\([^\/]+\)"

def can_handle(*args):
    return False

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

def read_options(options):
    try:
        base, file_pattern = options['data'].split(" ")[:2]
    except ValueError:
        base, file_pattern = options['data'], None

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

    return base, file_pattern

def scan_pkg(pkg, options):
    output.einfo("Using watch data")

    cp, ver, rev = pkg.cp, pkg.version, pkg.revision

    base, file_pattern = read_options(options)

    results = []
    if not re.search(is_pattern, base):
        steps = [(base, file_pattern)]
        results = generic.scan_directory_recursive(
            cp, ver, rev, "", steps, base, options
        )
    else:
        for step in handle_directory_patterns(base, file_pattern):
            results += generic.scan_directory_recursive(
                cp, ver, rev, "", [step], base, options
            )

    return results

