import sys
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from djeuscan.processing import set_verbosity_level
from djeuscan.processing.scan import scan_portage

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
        make_option('--purge-packages',
            action='store_true',
            dest='purge-packages',
            default=False,
            help='Purge old packages'),
        make_option('--purge-versions',
            action='store_true',
            dest='purge-versions',
            default=False,
            help='Purge old versions'),
        make_option('--upstream',
            action='store_true',
            dest='upstream',
            default=False,
            help='Scan upstream for updated packages in Portage'),
        make_option('--no-log',
            action='store_true',
            dest='no-log',
            default=False,
            help='Don\'t store logs'),
        )
    args = '[package package ...]'
    help = 'Scans portage tree and fills database'

    def handle(self, *args, **options):
        set_verbosity_level(logger, options.get("verbosity", 1))

        if options['all'] or options['category']:
            packages = None
        elif len(args):
            packages = [pkg for pkg in args]
        else:
            packages = [pkg[:-1] for pkg in sys.stdin.readlines()]

        scan_portage(
            packages=packages,
            category=options['category'],
            no_log=options["no-log"],
            purge_packages=options["purge-packages"],
            purge_versions=options["purge-versions"],
            upstream=options["upstream"],
            logger=logger,
        )
