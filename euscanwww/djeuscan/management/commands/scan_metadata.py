import sys

from optparse import make_option

from gentoolkit.query import Query
from gentoolkit.errors import GentoolkitFatalError

from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from djeuscan.models import Package, Herd, Maintainer


class ScanMetadata(object):
    def __init__(self, quiet):
        self.quiet = quiet

    @commit_on_success
    def run(self, query=None, obj=None):
        matches = Query(query).find(
            include_masked=True,
            in_installed=False,
        )

        if not matches:
            sys.stderr.write(
                color_style.ERROR("Unknown package '%s'\n" % query)
            )
            return

        matches = sorted(matches)
        pkg = matches.pop()
        if '9999' in pkg.version and len(matches):
            pkg = matches.pop()

        if not obj:
            obj, created = Package.objects.get_or_create(
                category=pkg.category, name=pkg.name
            )
        else:
            created = False

        try:
            obj.homepage = pkg.environment("HOMEPAGE")
            obj.description = pkg.environment("DESCRIPTION")
        except GentoolkitFatalError, err:
            sys.stderr.write(
                color_style.ERROR(
                    "Gentoolkit fatal error: '%s'\n" % str(err)
                )
            )

        if created and not self.quiet:
            sys.stdout.write('+ [p] %s/%s\n' % (pkg.category, pkg.name))

        if pkg.metadata:
            herds = dict(
                [(herd[0], herd) for herd in pkg.metadata.herds(True)]
            )
            maintainers = dict(
                [(m.email, m) for m in pkg.metadata.maintainers()]
            )

            existing_herds = [h.herd for h in obj.herds.all()]
            new_herds = set(herds.keys()).difference(existing_herds)
            old_herds = set(existing_herds).difference(herds.keys())

            existing_maintainers = [m.email for m in obj.maintainers.all()]
            new_maintainers = set(
                maintainers.keys()).difference(existing_maintainers
            )
            old_maintainers = set(
                existing_maintainers).difference(maintainers.keys()
            )

            for herd in obj.herds.all():
                if herd.herd in old_herds:
                    obj.herds.remove(herd)

            for herd in new_herds:
                herd = self.store_herd(*herds[herd])
                obj.herds.add(herd)

            for maintainer in obj.maintainers.all():
                if maintainer.email in old_maintainers:
                    obj.maintainers.remove(maintainer)

            for maintainer in new_maintainers:
                maintainer = maintainers[maintainer]
                maintainer = self.store_maintainer(
                    maintainer.name, maintainer.email
                )
                obj.maintainers.add(maintainer)

        obj.save()

    def store_herd(self, name, email):
        if not name:
            name = '{nil}'
        name = name.strip("\r").strip("\n").strip("\t").strip()

        herd, created = Herd.objects.get_or_create(
            herd=name,
            defaults={"email": email}
        )

        if created and not self.quiet:
            sys.stdout.write('+ [h] %s <%s>\n' % (name, email))

        herd.email = email
        herd.save()

        return herd

    def store_maintainer(self, name, email):
        if not name:
            name = email
        if not name:
            name = '{nil}'

        maintainer, created = Maintainer.objects.get_or_create(
            email=email,
            defaults={"name": name}
        )

        if created:
            if not self.quiet:
                sys.stdout.write(
                    '+ [m] %s <%s>\n' % (name.encode('utf-8'), email)
                )
        return maintainer


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Scan all packages'),
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
        )
    args = '<package package ...>'
    help = 'Scans metadata and fills database'

    def handle(self, *args, **options):
        self.options = options

        scan_metadata = ScanMetadata(quiet=options["quiet"])

        if options['all']:
            for pkg in Package.objects.all():
                scan_metadata.run('%s/%s' % (pkg.category, pkg.name), pkg)
        elif len(args) > 0:
            for package in args:
                scan_metadata.run(package)
        else:
            for package in sys.stdin.readlines():
                scan_metadata.run(package[:-1])
