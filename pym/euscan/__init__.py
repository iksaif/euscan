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
    'http://www.rennings.net/gentoo/distfiles/(.*)',  # Doesn't respect 404, infinite loop
    'http://art.gnome.org/download/(.*)',  # Doesn't respect 404, infinite loop
    'http://barelysufficient.org/~olemarkus/(.*)',  # Doesn't respect 404, infinite loop
    'http://olemarkus.org/~olemarkus/(.*)',  # Doesn't respect 404, infinite loop
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
        self.data = defaultdict(StringIO)
        self.packages = defaultdict(list)

    def get_formatted_output(self):
        data = {}
        for key in self.data:
            if key not in ("ebegin", "eend"):
                val = [x for x in self.data[key].getvalue().split("\n") if x]
                data[key] = val

        data["result"] = self.packages

        if self.config["format"].lower() == "json":
            return json.dumps(data, indent=self.config["indent"])
        else:
            raise TypeError("Invalid output format")

    def result(self, cp, version, url):
        if self.config['format']:
            self.packages[cp].append({"version": version, "url": url})
        else:
            if not self.config['quiet']:
                print "Upstream Version:", pp.number("%s" % version),
                print pp.path(" %s" % url)
            else:
                print pp.cpv("%s-%s" % (cp, version)) + ":", pp.path(url)

    def __getattr__(self, key):
        output_file = self.data[key] if self.config["format"] else None

        if output_file:
            _output = EOutputFile(out_file=self.data[key],
                                  quiet=self.config['quiet'])
            ret = getattr(_output, key)
        else:
            ret = getattr(EOutputFile(quiet=self.config['quiet']), key)

        return ret


output = EuscanOutput(CONFIG)
