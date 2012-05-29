import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from djeuscan.models import Package


def list_packages(stdout=None, **options):
    if stdout is None:
        stdout = sys.stdout

    after = None
    before = None

    if options['after']:
        category, name = options['after'].split('/')
        after = Package.objects.get(category=category, name=name)

    if options['before']:
        category, name = options['before'].split('/')
        before = Package.objects.get(category=category, name=name)

    packages = Package.objects

    if after or before:
        if after:
            packages = packages.filter(id__gte=after.id)
        if before:
            packages = packages.filter(id__lte=before.id)
    else:
        packages = packages.all()

    if options['limit']:
        packages = packages[:int(options['limit'])]

    for pkg in packages:
        stdout.write('%s/%s\n' % (pkg.category, pkg.name))
    stdout.close()


class Command(BaseCommand):
    _overlays = {}
    help = 'List packages'

    option_list = BaseCommand.option_list + (
        make_option('--after',
            action='store',
            dest='after',
            default=False,
            help='After package'),
        make_option('--before',
            action='store',
            dest='before',
            default=False,
            help='Before package'),
        make_option('--limit',
            action='store',
            dest='limit',
            default=False,
            help='limit'),
        )

    def handle(self, *args, **options):
        list_packages(self.stdout, **options)
