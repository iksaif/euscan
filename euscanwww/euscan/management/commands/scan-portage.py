import subprocess
import portage
import sys
import os
import re

from portage import versions
from optparse import make_option

from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand, CommandError
from euscanwww.euscan.models import Package, Version

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
    help = 'Scans portage tree and fills database'

    def handle(self, *args, **options):
        if len(args) == 0 and options['all'] == False:
            raise CommandError('You must specify a package or use --all')

        if not options['quiet']:
            self.stdout.write('Scanning portage tree...\n')

        for package in args:
            self.scan(options, package)

        if len(args) == 0:
            self.scan(options)

        if not options['quiet']:
            self.stdout.write('Done.\n')

    def overlays(self):
        if self._overlays:
            return self._overlays

        env = os.environ
        env['OVERLAYS_LIST'] = 'all'
        env['PRINT_COUNT_ALWAYS'] = 'never'

        cmd = ['eix', '-!']

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        output = output.strip().strip('\n').split('\n')

        overlay_re = re.compile(r'^\[(?P<key>\d+)] "(?P<name>.*?)"')

        self._overlays = {}

        for line in output:
            match = overlay_re.match(line)
            if not match:
                continue
            self._overlays[match.group('key')] = match.group('name')

        return self._overlays

    @commit_on_success
    def scan(self, options, query=None):
        env = os.environ
        env['MY'] = "<category>/<name>-<version>:<slot> [<overlaynum>]\n"

	cmd = ['eix', '--format', '<availableversions:MY>', '--pure-packages', '-x']
	if query:
		cmd.extend(['--exact', query])

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        output = output.strip().strip('\n')

        if len(output) == 0:
            if package:
                sys.stderr.write(self.style.ERROR("Unknown package '%s'\n" % package))
            return

	output = output.split('\n')

        line_re = re.compile(r'^(?P<cpv>.*?):(?P<slot>.*?) \[(?P<overlay>.*?)\]$')

        package = None

	for line in output:
            match = line_re.match(line)

            if not match:
                continue

            cpv = match.group('cpv')
            slot = match.group('slot')
            overlay = match.group('overlay')

            if not package or not cpv.startswith(str(package)):
                package = self.store_package(options, cpv)

            self.store_version(options, package, cpv, slot, overlay)

    def store_package(self, options, cpv):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)

        obj, created = Package.objects.get_or_create(category=cat, name=pkg)

        if created:
            if not options['quiet']:
                sys.stdout.write('[p] %s/%s\n' % (cat, pkg))

        # Delete previous versions to handle incremental scan correctly
        Version.objects.filter(package=obj, packaged=True).delete()

        obj.n_versions = Version.objects.filter(package=obj).count()
        obj.save()

        return obj

    def store_version(self, options, package, cpv, slot, overlay):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)

        overlays = self.overlays()

        if overlay in overlays:
            overlay = overlays[overlay]
        else:
            overlay = 'gentoo'

        if not options['quiet']:
            sys.stdout.write('[v] %s:%s [%s]\n' % (cpv, slot, overlay))

        obj, created = Version.objects.get_or_create(package=package, slot=slot,
                                                     revision=rev, version=ver,
                                                     overlay=overlay)
        obj.packaged = True
        obj.save()

        package.n_versions += 1
        package.n_packaged += 1
        package.save()
