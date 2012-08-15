#!/usr/bin/env python

from __future__ import print_function

import re
import sys
from distutils import log
try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command
from glob import glob

import os
from os.path import join, dirname
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pym'))

__version__ = os.getenv('VERSION', default='9999')

cwd = os.getcwd()

# Load EPREFIX from Portage, fall back to the empty string if it fails
try:
    from portage.const import EPREFIX
except ImportError:
    EPREFIX = ''

# Python files that need `__version__ = ""` subbed, relative to this dir:
python_scripts = [os.path.join(cwd, path) for path in (
    'bin/euscan',
)]


class set_version(Command):
    """Set python __version__ to our __version__."""
    description = "hardcode scripts' version using VERSION from environment"
    user_options = []  # [(long_name, short_name, desc),]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        ver = 'git' if __version__ == '9999' else __version__
        print("Settings version to %s" % ver)

        def sub(files, pattern):
            for f in files:
                updated_file = []
                with io.open(f, 'r', 1, 'utf_8') as s:
                    for line in s:
                        newline = re.sub(pattern, '"%s"' % ver, line, 1)
                        if newline != line:
                            log.info("%s: %s" % (f, newline))
                        updated_file.append(newline)
                with io.open(f, 'w', 1, 'utf_8') as s:
                    s.writelines(updated_file)
        quote = r'[\'"]{1}'
        python_re = r'(?<=^__version__ = )' + quote + '[^\'"]*' + quote
        sub(python_scripts, python_re)

packages = [
    str('.'.join(root.split(os.sep)[1:]))
    for root, dirs, files in os.walk('pym/euscan')
    if '__init__.py' in files
]

tests_require = [
  'factory-boy>=1.1.3',
]

setup(
    name='euscan',
    version=__version__,
    description='Ebuild upstream scan utility.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author='Corentin Chary',
    author_email='corentin.chary@gmail.com',
    maintainer='Corentin Chary',
    maintainer_email='corentin.chary@gmail.com',
    url='http://euscan.iksaif.net',
    download_url=(
        'https://github.com/iksaif/euscan/tarball/' +
        ('master' if __version__ == '9999' else ('euscan-%s' % __version__))
    ),
    install_requires=[
        # Command line utility
        'BeautifulSoup>=3.2.1',
        # Web interface
        'Django>=1.4', 'django-annoying>=0.7.6', 'South>=0.7',
        'django-piston>=0.2.3', 'matplotlib>=1.1.0',
        'django-celery>=3.0.1', 'django-registration>=0.8',
        'python-ldap>=2.4.10', 'django-auth-ldap>=1.1',
        'django-recaptcha>=0.0.4', 'ansi2html>=0.9.1',
    ],
    package_dir={'': 'pym'},
    packages=packages,
    package_data={},
    scripts=python_scripts,
    data_files=(
        (os.path.join(os.sep, EPREFIX.lstrip(os.sep), 'usr/share/man/man1'),
        glob('man/*')),
    ),
    cmdclass={
        'set_version': set_version,
    },
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='euscanwww.runtests.runtests',
)
