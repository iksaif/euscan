from django.core.management.base import BaseCommand, CommandError
from euscanwww.euscan.models import Package

class Command(BaseCommand):
    _overlays = {}
    help = 'List packages'

    def handle(self, *args, **options):
        for pkg in Package.objects.all():
            self.stdout.write('%s/%s\n' % (pkg.category, pkg.name))
