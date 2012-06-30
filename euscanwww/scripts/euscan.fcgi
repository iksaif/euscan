#!/usr/bin/python

import sys
import os
import os.path

PROJECT = '/path/to/euscanwww'

sys.path.insert(0, os.path.dirname(PROJECT))
sys.path.insert(0, PROJECT)

os.chdir(PROJECT)

os.environ['DJANGO_SETTINGS_MODULE'] = "euscanwww.settings"
os.environ['HOME'] = "/path/to/home"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false", maxspare=1)
