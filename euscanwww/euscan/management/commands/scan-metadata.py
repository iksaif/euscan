import subprocess
import portage
import sys
import os
import re

from portage import versions
from optparse import make_option

from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand, CommandError
from euscanwww.euscan.models import Package, Herd, Maintainer

from gentoolkit.query import Query
from gentoolkit.errors import GentoolkitFatalError

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

    @commit_on_success
    def handle(self, *args, **options):
        self.options = options

        if options['all']:
            for pkg in Package.objects.all():
                self.scan('%s/%s' % (pkg.category, pkg.name), pkg)
        elif len(args):
            for package in args:
                self.scan(package)
        else:
            for package in sys.stdin.readlines():
                self.scan(package[:-1])

    def scan(self, query=None, obj=None):
        matches = Query(query).find(
            include_masked=True,
            in_installed=False,
        )

        if not matches:
            sys.stderr.write(self.style.ERROR("Unknown package '%s'\n" % query))
            return

	matches = sorted(matches)
        pkg = matches.pop()
	if '9999' in pkg.version and len(matches):
            pkg = matches.pop()

        if not obj:
            obj, created = Package.objects.get_or_create(category=pkg.category, name=pkg.name)
        else:
            created = False

        try:
            obj.homepage = pkg.environment("HOMEPAGE")
            obj.description = pkg.environment("DESCRIPTION")
        except GentoolkitFatalError, err:
            sys.stderr.write(self.style.ERROR("Gentoolkit fatal error: '%s'\n" % str(err)))

        if created and not self.options['quiet']:
            sys.stdout.write('+ [p] %s/%s\n' % (pkg.category, pkg.name))

        if pkg.metadata:
            herds = dict([(herd[0], herd) for herd in pkg.metadata.herds(True)])
            maintainers = dict([(m.email, m) for m in pkg.metadata.maintainers()])

            existing_herds = [h.herd for h in obj.herds.all()]
            new_herds = set(herds.keys()).difference(existing_herds)
            old_herds = set(existing_herds).difference(herds.keys())

            existing_maintainers = [m.email for m in obj.maintainers.all()]
            new_maintainers = set(maintainers.keys()).difference(existing_maintainers)
            old_maintainers = set(existing_maintainers).difference(maintainers.keys())

            for herd in obj.herds.all():
                if herd.email in old_herds:
                    obj.herds.remove(herd)

            for herd in new_herds:
                herd = self.store_herd(*herds[herd])
                obj.herds.add(herd)

            for maintainer in obj.maintainers.all():
                if maintainer.email in old_maintainers:
                    obj.maintainers.remove(maintainer)

            for maintainer in new_maintainers:
                maintainer = maintainers[maintainer]
                maintainer = self.store_maintainer(maintainer.name, maintainer.email)
                obj.maintainers.add(maintainer)

        obj.save()

    def store_herd(self, name, email):
        if not name:
            name = '{nil}'
        name = name.strip("\r").strip("\n").strip("\t").strip()

        herd, created = Herd.objects.get_or_create(herd=name)

        if created and not self.options['quiet']:
            sys.stdout.write('+ [h] %s <%s>\n' % (name, email))

        herd.email = email
        herd.save()

        return herd

    def store_maintainer(self, name, email):
        if not name:
            name = email
        if not name:
            name = '{nil}'

        maintainer, created = Maintainer.objects.get_or_create(email=email)

        if created:
            if not self.options['quiet']:
                sys.stdout.write('+ [m] %s <%s>\n' % (name.encode('utf-8'), email))

            if not maintainer.name or name not in [maintainer.name, email, '{nil}']:
                maintainer.name = name
            maintainer.save()

        return maintainer
