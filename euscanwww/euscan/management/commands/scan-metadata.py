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

    def handle(self, *args, **options):
        if len(args) == 0 and options['all'] == False:
            raise CommandError('You must specify a package or use --all')

        if len(args) == 0:
            for pkg in Package.objects.all():
                self.scan(options, '%s/%s' % (pkg.category, pkg.name))
        else:
            for package in args:
                self.scan(options, package)

    @commit_on_success
    def scan(self, options, query=None):
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

        obj, created = Package.objects.get_or_create(category=pkg.category, name=pkg.name)

        try:
            obj.homepage = pkg.environment("HOMEPAGE")
            obj.description = pkg.environment("DESCRIPTION")
        except GentoolkitFatalError, err:
            sys.stderr.write(self.style.ERROR("Gentoolkit fatal error: '%s'\n" % str(err)))

        if created and not options['quiet']:
            sys.stdout.write('+ [p] %s/%s\n' % (pkg.category, pkg.name))
        if pkg.metadata:
            obj.herds.clear()
            obj.maintainers.clear()

            for herd in pkg.metadata.herds(True):
                herd = self.store_herd(options, herd[0], herd[1])
                obj.herds.add(herd)

            for maintainer in pkg.metadata.maintainers():
                maintainer = self.store_maintainer(options, maintainer.name, maintainer.email)
                obj.maintainers.add(maintainer)

        obj.save()

    def store_herd(self, options, name, email):
        if not name:
            name = '{nil}'
        name = name.strip("\r").strip("\n").strip("\t").strip()

        herd, created = Herd.objects.get_or_create(herd=name)

        if created and not options['quiet']:
            sys.stdout.write('+ [h] %s <%s>\n' % (name, email))

        herd.email = email
        herd.save()

        return herd

    def store_maintainer(self, options, name, email):
        if not name:
            name = email
        if not name:
            name = '{nil}'

        maintainer, created = Maintainer.objects.get_or_create(email=email)

        if created:
            if not options['quiet']:
                sys.stdout.write('+ [m] %s <%s>\n' % (name.encode('utf-8'), email))

            maintainer.name = name
            maintainer.save()

        return maintainer
