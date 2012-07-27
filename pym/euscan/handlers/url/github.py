import json
import urllib2
import re

import portage

from euscan import helpers, output

HANDLER_NAME = "github"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url):
    return url.startswith('mirror://github/')


def guess_package(cp, url):
    match = re.search('^mirror://github/(.*?)/(.*?)/(.*)$', url)

    assert(match)
    return (match.group(1), match.group(2), match.group(3))


def scan(pkg, url):
    'http://developer.github.com/v3/repos/downloads/'

    user, project, filename = guess_package(pkg.cpv, url)

    # find out where version is expected to be found
    cp, ver, rev = portage.pkgsplit(pkg.cpv)
    if ver not in filename:
        return

    # now create a filename-matching regexp
    # XXX: supposedly replace first with (?P<foo>...)
    # and remaining ones with (?P=foo)
    fnre = re.compile('^%s$' % \
                      re.escape(filename).replace(re.escape(ver), '(.*?)'))

    output.einfo("Using github API for: " + '/'.join(filename))

    dlreq = urllib2.urlopen('https://api.github.com/repos/%s/%s/downloads' % \
                            (user, project))
    dls = json.load(dlreq)

    ret = []
    for dl in dls:
        m = fnre.match(dl['name'])

        if m:
            pv = helpers.gentoo_mangle_version(m.group(1))
            if helpers.version_filtered(cp, ver, pv):
                continue

            ret.append((dl['html_url'], pv, HANDLER_NAME, CONFIDENCE))
    return ret
