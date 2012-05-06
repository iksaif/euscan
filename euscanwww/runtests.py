"""
Runner for tests
"""

import sys
import os
from os.path import dirname, abspath
from django.conf import settings

settings.configure(
    DATABASES={
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory;'}
    },
    INSTALLED_APPS=['euscanwww', 'djeuscan'],
    ROOT_URLCONF='euscanwww.euscanwww.urls',
    EUSCAN_ROOT=os.path.join(dirname(dirname(abspath(__file__))), "euscanwww"),
)


def runtests():
    import django.test.utils

    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    runner_class = django.test.utils.get_runner(settings)
    test_runner = runner_class(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['djeuscan'])

    sys.exit(failures)
