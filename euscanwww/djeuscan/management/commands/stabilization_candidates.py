import logging
from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.misc import stabilization_candidates

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    _overlays = {}
    help = 'Collect stabilization candidates'

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))
        stabilization_candidates(logger=logger)