import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.update_counters import update_counters

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    _overlays = {}
    help = 'Update counters'

    option_list = BaseCommand.option_list + (
        make_option('--fast',
            action='store_true',
            dest='fast',
            default=False,
            help='Skip sanity checks'),
        make_option('--nolog',
            action='store_true',
            dest='nolog',
            default=False,
            help='Skip logs'),
    )

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))
        update_counters(
            fast=options["fast"],
            nolog=options["nolog"],
            logger=logger,
        )
