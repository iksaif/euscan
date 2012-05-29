from django.core.management.base import BaseCommand
from djeuscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from djeuscan import charts


def regen_rrds():
    """
    Regenerates the rrd database
    """
    for wlog in WorldLog.objects.all():
        charts.rrd_update('world', wlog.datetime, wlog)

    for clog in CategoryLog.objects.all():
        charts.rrd_update('category-%s' % clog.category,
                          clog.datetime, clog)

    for hlog in HerdLog.objects.all():
        charts.rrd_update('herd-%d' % hlog.herd.id, hlog.datetime, hlog)

    for mlog in MaintainerLog.objects.all():
        charts.rrd_update('maintainer-%d' % mlog.maintainer.id,
                          mlog.datetime, mlog)


class Command(BaseCommand):
    _overlays = {}
    help = 'Regenerate rrd database'

    def handle(self, *args, **options):
        regen_rrds()
