from djeuscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from djeuscan import charts

from djeuscan.processing import FakeLogger

def regen_rrds(logger=None):
    """
    Regenerates the rrd database
    """

    if logger is None:
        logger = FakeLogger()

    logger.info("Regenering RRDs for world")
    for wlog in WorldLog.objects.all():
        charts.rrd_update('world', wlog.datetime, wlog)

    logger.info("Regenering RRDs for categories")
    for clog in CategoryLog.objects.all():
        charts.rrd_update('category-%s' % clog.category,
                          clog.datetime, clog)

    logger.info("Regenering RRDs for herds")
    for hlog in HerdLog.objects.all():
        charts.rrd_update('herd-%d' % hlog.herd.id, hlog.datetime, hlog)

    logger.info("Regenering RRDs for maintainers")
    for mlog in MaintainerLog.objects.all():
        charts.rrd_update('maintainer-%d' % mlog.maintainer.id,
                          mlog.datetime, mlog)
