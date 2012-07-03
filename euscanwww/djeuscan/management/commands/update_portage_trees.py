import logging
from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.misc import update_portage_trees

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    _overlays = {}
    help = 'Regenerate rrd database'

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))
        update_portage_trees(logger=logger)
