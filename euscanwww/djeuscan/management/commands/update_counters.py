from optparse import make_option

from django.core.management.base import BaseCommand

from djeuscan.processing.update_counters import update_counters


class Command(BaseCommand):
    _overlays = {}
    help = 'Update counters'

    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
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
        update_counters(
            stdout=self.stdout,
            fast=options["fast"],
            quiet=options["quiet"],
            nolog=options["nolog"],
        )
