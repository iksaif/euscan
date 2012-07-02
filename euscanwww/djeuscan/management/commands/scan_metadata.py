import sys
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.scan_metadata import scan_metadata

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Scan all packages'),
        make_option('--category',
            action='store',
            dest='category',
            default=None,
            help='Scan only this category'),
        )
    args = '<package package ...>'
    help = 'Scans metadata and fills database'

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))

        if options['all'] or options['category']:
            packages = None

        elif len(args):
            packages = [pkg for pkg in args]
        else:
            packages = [pkg[:-1] for pkg in sys.stdin.readlines()]

        scan_metadata(
            packages=packages,
            category=options['category'],
            logger=logger
        )
