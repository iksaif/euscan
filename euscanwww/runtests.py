"""
Runner for tests
"""

import sys
import os
from os.path import dirname, abspath
from django.conf import settings

EUSCAN_ROOT = os.path.join(dirname(dirname(abspath(__file__))), "euscanwww")

settings.configure(
    DATABASES={
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
    },
    INSTALLED_APPS=[
        'euscanwww.euscanwww',
        'djeuscan',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.admin',
        'django.contrib.sessions',
        'django.contrib.sites',
    ],
    SITE_ID=1,
    ROOT_URLCONF='euscanwww.euscanwww.urls',
    EUSCAN_ROOT=EUSCAN_ROOT,
    RRD_ROOT=os.path.join(EUSCAN_ROOT, 'var', 'rrd'),
    USE_TZ=True,
    TASKS_CONCURRENTLY=8,
    TASKS_SUBTASK_PACKAGES=32,
    AUTH_PROFILE_MODULE="djeuscan.UserProfile"
)


def runtests():
    import django.test.utils

    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    runner_class = django.test.utils.get_runner(settings)
    test_runner = runner_class(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['djeuscan'])

    sys.exit(failures)
