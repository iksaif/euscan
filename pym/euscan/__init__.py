#!/usr/bin/python
#
# Copyright 2011 Corentin Chary <corentin.chary@gmail.com>
# Distributed under the terms of the GNU General Public License v2

import sys

from portage.output import EOutput

CONFIG = {
    'nocolor': False,
    'quiet': False,
    'verbose': True,
    'debug': False,
    'brute-force': 3,
    'brute-force-recursive': True,
    'scan-dir': True,
    'oneshot': False,
    'user-agent' : 'Mozilla/5.0 (compatible; euscan; +http://euscan.iksaif.net)',
    'skip-robots-txt' : False
}

output = EOutput(CONFIG['quiet'])

BLACKLIST_VERSIONS = [
	# Compatibility package for running binaries linked against a pre gcc 3.4 libstdc++, won't be updated
	'>=sys-libs/libstdc++-v3-3.4',
]

BLACKLIST_PACKAGES = [
	# These kernels are almost dead
	'sys-kernel/usermode-sources',
	'sys-kernel/xbox-sources',
	'sys-kernel/cell-sources',
]

SCANDIR_BLACKLIST_URLS = [
	'mirror://rubygems/(.*)', # Not browsable
	'mirror://gentoo/(.*)' # Directory too big
]

BRUTEFORCE_BLACKLIST_PACKAGES = [
	'net-zope/plonepopoll' # infinite loop any http://plone.org/products/plonepopoll/releases/*/plonepopoll-2-6-1.tgz link will work
	]

BRUTEFORCE_BLACKLIST_URLS = [
	'http://(.*)dockapps.org/download.php/id/(.*)', # infinite loop
	'http://hydra.nixos.org/build/(.*)', # infinite loop
	'http://www.rennings.net/gentoo/distfiles/(.*)' # Doesn't respect 404, infinite loop
]
