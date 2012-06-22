from django.core.management.base import BaseCommand
from djeuscan.processing.regen_rrds import regen_rrds


class Command(BaseCommand):
    _overlays = {}
    help = 'Regenerate rrd database'

    def handle(self, *args, **options):
        regen_rrds()
