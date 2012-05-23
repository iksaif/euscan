#!/usr/bin/python
#
# Copyright 2011 Corentin Chary <corentin.chary@gmail.com>
# Distributed under the terms of the GNU General Public License v2

from io import StringIO
from collections import defaultdict
import json

from gentoolkit import pprinter as pp
from portage.output import EOutput


__version__ = "git"


CONFIG = {
    'nocolor': False,
    'quiet': False,
    'verbose': 1,
    'debug': False,
    'brute-force': 3,
    'brute-force-recursive': True,
    'brute-force-false-watermark': 50,
    'scan-dir': True,
    'oneshot': True,
    'user-agent': 'escan (http://euscan.iksaif.net)',
    'skip-robots-txt': False,
    'cache': False,
    'format': None,
    'indent': 2
}

BLACKLIST_VERSIONS = [
    # Compatibility package for running binaries linked against a
    # pre gcc 3.4 libstdc++, won't be updated
    '>=sys-libs/libstdc++-v3-3.4',
]

BLACKLIST_PACKAGES = [
    # These kernels are almost dead
    'sys-kernel/usermode-sources',
    'sys-kernel/xbox-sources',
    'sys-kernel/cell-sources',
]

SCANDIR_BLACKLIST_URLS = [
    'mirror://rubygems/(.*)',  # Not browsable
    'mirror://gentoo/(.*)'  # Directory too big
]

BRUTEFORCE_BLACKLIST_PACKAGES = [
    # infinite loop any
    # http://plone.org/products/plonepopoll/releases/*/plonepopoll-2-6-1.tgz
    # link will work
    'net-zope/plonepopoll'
]

BRUTEFORCE_BLACKLIST_URLS = [
    'http://(.*)dockapps.org/download.php/id/(.*)',  # infinite loop
    'http://hydra.nixos.org/build/(.*)',  # infinite loop
    # Doesn't respect 404, infinite loop
    'http://www.rennings.net/gentoo/distfiles/(.*)',
    'http://art.gnome.org/download/(.*)',
    'http://barelysufficient.org/~olemarkus/(.*)',
    'http://olemarkus.org/~olemarkus/(.*)',
]

ROBOTS_TXT_BLACKLIST_DOMAINS = [
    '(.*)sourceforge(.*)',
    '(.*)github.com',
    '(.*)berlios(.*)',
    '(.*)qt.nokia.com(.*)',
    '(.*)chromium.org(.*)',
    '(.*)nodejs.org(.*)',
]


class EOutputFile(EOutput):
    """
    Override of EOutput, allows to specify an output file for writes
    """
    def __init__(self, out_file=None, *args, **kwargs):
        super(EOutputFile, self).__init__(*args, **kwargs)
        self.out_file = out_file

    def _write(self, f, msg):
        if self.out_file is None:
            super(EOutputFile, self)._write(f, msg)
        else:
            super(EOutputFile, self)._write(self.out_file, msg)


class EuscanOutput(object):
    """
    Class that handles output for euscan
    """
    def __init__(self, config):
        self.config = config
        self.queries = defaultdict(dict)
        self.current_query = None

    def set_query(self, query):
        self.current_query = query
        if query is not None:
            if not query in self.queries:
                self.queries[query] = {
                    "messages": defaultdict(StringIO),
                    "result": [],
                    "metadata": {},
                }

    def get_formatted_output(self):
        data = {}

        for query in self.queries:
            data[query] = {
                "result": self.queries[query]["result"],
                "metadata": self.queries[query]["metadata"],
                "messages": {}
            }
            for key in self.queries[query]["messages"]:
                if key not in ("ebegin", "eend"):
                    _msg = self.queries[query]["messages"][key].getvalue()
                    val = [x for x in _msg.split("\n") if x]
                    data[query]["messages"][key] = val

        if self.config["format"].lower() == "json":
            return json.dumps(data, indent=self.config["indent"])
        else:
            raise TypeError("Invalid output format")

    def result(self, cp, version, url, handler):
        if self.config['format']:
            _curr = self.queries[self.current_query]
            _curr["result"].append(
                {"version": version, "urls": [url], "handler": handler}
            )
        else:
            if not self.config['quiet']:
                print "Upstream Version:", pp.number("%s" % version),
                print pp.path(" %s" % url)
            else:
                print pp.cpv("%s-%s" % (cp, version)) + ":", pp.path(url)

    def metadata(self, key, value, show=True):
        if self.config["format"]:
            self.queries[self.current_query]["metadata"][key] = value
        elif show:
            print "%s: %s" % (key.capitalize(), value)

    def __getattr__(self, key):
        if self.config["format"]:
            out_file = self.queries[self.current_query]["messages"][key]

            _output = EOutputFile(out_file=out_file,
                                  quiet=self.config['quiet'])
            ret = getattr(_output, key)
        else:
            ret = getattr(EOutputFile(quiet=self.config['quiet']), key)
        return ret


output = EuscanOutput(CONFIG)
