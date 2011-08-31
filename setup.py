#!/usr/bin/env python

from __future__ import print_function

import re
import sys
import distutils
from distutils import core, log
from glob import glob

import os
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pym'))

__version__ = os.getenv('VERSION', default='9999')

cwd = os.getcwd()

# Load EPREFIX from Portage, fall back to the empty string if it fails
try:
	from portage.const import EPREFIX
except ImportError:
	EPREFIX='/'

# Python files that need `__version__ = ""` subbed, relative to this dir:
python_scripts = [os.path.join(cwd, path) for path in (
	'bin/euscan',
)]

packages = [
	str('.'.join(root.split(os.sep)[1:]))
	for root, dirs, files in os.walk('pym/euscan')
	if '__init__.py' in files
]

core.setup(
	name='euscan',
	version=__version__,
	description='Ebuild Upstream Scan tools.',
	author='Corentin Chary',
	author_email='corentin.chary@gmail.com',
	maintainer='Corentin Chary',
	maintainer_email='corentin.chary@gmail.com',
	url='http://euscan.iksaif.net',
	download_url='http://git.iksaif.net/?p=euscan.git;a=snapshot;h=HEAD;sf=tgz',
	package_dir={'': 'pym'},
	packages=packages,
	package_data = {},
	scripts=python_scripts,
	data_files=(
		(os.path.join(EPREFIX, 'usr/share/man/man1'), glob('man/*')),
	),
)
