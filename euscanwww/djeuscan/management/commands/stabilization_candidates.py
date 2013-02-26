import logging
from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.misc import stabilization_candidates
from optparse import make_option

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option(
            '-d',
            '--days-to-candidate',
            action='store_true',
            dest='all',
            default=30,
            help='Minimum of days to be in tree for becoming stable.'
        ),
    )
    help = 'Collects stabilization candidates'

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))
        stabilization_candidates(logger=logger)