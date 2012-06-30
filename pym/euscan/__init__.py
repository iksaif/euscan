#!/usr/bin/python
#
# Copyright 2011 Corentin Chary <corentin.chary@gmail.com>
# Distributed under the terms of the GNU General Public License v2

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
    'indent': 2,
    'progress': False
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
    '(.*)download.mono-project.com(.*)',
]

from out import EuscanOutput
output = EuscanOutput(CONFIG)
