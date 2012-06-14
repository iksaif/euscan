import json, urllib2
import re

import portage

from euscan import helpers, output

HANDLER_NAME = "github"
CONFIDENCE = 100.0

def can_handle(cpv, url):
    return url.startswith('mirror://github/')

def guess_package(cp, url):
    match = re.search('^mirror://github/(.*?)/(.*?)/(.*)$', url)

    assert(match)
    return (match.group(1), match.group(2), match.group(3))

def scan(cpv, url):
    'http://developer.github.com/v3/repos/downloads/'

    user, project, filename = guess_package(cpv, url)

    # find out where version is expected to be found
    cp, ver, rev = portage.pkgsplit(cpv)
    if ver not in filename:
        return

    # now create a filename-matching regexp
    # XXX: supposedly replace first with (?P<foo>...)
    # and remaining ones with (?P=foo)
    fnre = re.compile('^%s$' % re.escape(filename).replace(re.escape(ver), '(.*?)'))

    output.einfo("Using github API for: " + '/'.join(package))

    dlreq = urllib2.urlopen('https://api.github.com/repos/%s/%s/downloads' % (user, project))
    dls = json.load(dlreq)

    for dl in dls:
        m = fnre.match(dl['name'])

        if m:
            pv = helpers.gentoo_mangle_version(m.group(1))
            if helpers.version_filtered(cp, ver, pv):
                continue
            yield (dl['html_url'], pv, HANDLER_NAME, CONFIDENCE)

def brute_force(cpv, url):
    return []
