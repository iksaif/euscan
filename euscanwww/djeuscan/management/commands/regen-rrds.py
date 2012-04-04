import datetime

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from djeuscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from djeuscan import charts

class Command(BaseCommand):
    _overlays = {}
    help = 'Regenerate rrd database'

    def handle(self, *args, **options):
        for wlog in WorldLog.objects.all():
            charts.rrd_update('world', wlog.datetime, wlog)

        for clog in CategoryLog.objects.all():
            charts.rrd_update('category-%s' % clog.category, clog.datetime, clog)

        for hlog in HerdLog.objects.all():
            charts.rrd_update('herd-%d' % hlog.herd.id, hlog.datetime, hlog)

        for mlog in MaintainerLog.objects.all():
            charts.rrd_update('maintainer-%d' % mlog.maintainer.id, mlog.datetime, mlog)
