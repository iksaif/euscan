import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from djeuscan.processing.scan_upstream import scan_upstream


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Scan all packages'),
        make_option('--purge-versions',
            action='store_true',
            dest='purge-versions',
            default=False,
            help='Purge old versions'),
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
        )
    args = '<package package ...>'
    help = 'Scans metadata and fills database'

    def handle(self, *args, **options):
        if options['all']:
            packages = None

        elif len(args):
            packages = [pkg for pkg in args]
        else:
            packages = [pkg[:-1] for pkg in sys.stdin.readlines()]

        scan_upstream(
            packages=packages,
            purge_versions=options["purge-versions"],
            quiet=options["quiet"],
            stdout=self.stdout,
        )
