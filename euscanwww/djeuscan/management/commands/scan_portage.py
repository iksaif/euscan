import subprocess
import portage
import sys
import os
import re

from optparse import make_option

from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from djeuscan.models import Package, Version, VersionLog


class ScanPortage(object):
    def __init__(self, stdout=None, **options):
        if stdout is None:
            self.stdout = sys.stdout
        else:
            self.stdout = stdout

        self.options = options
        self.style = color_style()
        self._cache = {'packages': {}, 'versions': {}}
        self._overlays = None

    def cache_hash_package(self, category, name):
        return '%s/%s' % (category, name)

    def cache_store_package(self, package):
        key = self.cache_hash_package(package.category, package.name)
        self._cache['packages'][key] = package

    def cache_get_package(self, category, name):
        return self._cache['packages'].get(
            self.cache_hash_package(category, name)
        )

    def cache_hash_version(self, category, name, version, revision, slot,
                           overlay):
        key = '%s/%s-%s-r%s %s %s' % (category, name,
                                      version, revision,
                                      slot, overlay)
        return key

    def cache_get_version(self, category, name, version, revision, slot,
                          overlay):
        key = self.cache_hash_version(category, name, version, revision, slot,
                                      overlay)
        return self._cache['versions'].get(key)

    def cache_store_version(self, version):
        key = self.cache_hash_version(
            version.package.category, version.package.name, version.version,
            version.revision, version.slot, version.overlay
        )
        self._cache['versions'][key] = version

    def overlays(self):
        if self._overlays:
            return self._overlays

        env = os.environ
        env['OVERLAYS_LIST'] = 'all'
        env['PRINT_COUNT_ALWAYS'] = 'never'

        cmd = ['eix', '-!']

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).\
            communicate()[0]
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
    def run(self, query=None):
        env = os.environ
        env['MY'] = "<category>/<name>-<version>:<slot> [<overlaynum>]\n"

        cmd = ['eix', '--format', '<availableversions:MY>', '--pure-packages',
               '-x']
        if query:
            cmd.extend(['--exact', query])

        if self.options['all']:
            if not self.options['quiet']:
                self.stdout.write('Killing existing versions...')
                self.stdout.flush()
            Version.objects.filter(packaged=True).update(alive=False)
            if not self.options['quiet']:
                self.stdout.write('done\n')

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).\
            communicate()[0]
        output = output.strip().strip('\n')

        if len(output) == 0:
            if not query:
                return
            if self.options['purge-packages']:
                if not self.options['quiet']:
                    sys.stdout.write('- [p] %s\n' % (query))
                if '/' in query:
                    cat, pkg = portage.catsplit(query)
                    Package.objects.filter(category=cat, name=pkg).delete()
                else:
                    Package.objects.filter(name=query).delete()
            else:
                sys.stderr.write(
                    self.style.ERROR(
                        "Unknown package '%s'\n" % query
                    )
                )
            return

        output = output.split('\n')
        packages = {}

        line_re = re.compile(
            r'^(?P<cpv>.*?):(?P<slot>.*?) \[(?P<overlay>.*?)\]$'
        )

        package = None

        for line in output:
            match = line_re.match(line)

            if not match:
                continue

            cpv = match.group('cpv')
            slot = match.group('slot')
            overlay = match.group('overlay')

            cat, pkg, ver, rev = portage.catpkgsplit(cpv)

            packages['%s/%s' % (cat, pkg)] = True

            if not package or not \
               (cat == package.category and pkg == package.name):
                package = self.store_package(cat, pkg)

            self.store_version(package, cpv, slot, overlay)

        if self.options['purge-packages'] and not query:
            for package in Package.objects.all():
                cp = "%s/%s" % (package.category, package.name)
                if cp not in packages:
                    if not self.options['quiet']:
                        sys.stdout.write('- [p] %s\n' % (package))
                    package.delete()

    def store_package(self, cat, pkg):
        created = False
        obj = self.cache_get_package(cat, pkg)

        if not obj:
            obj, created = Package.objects.get_or_create(
                category=cat,
                name=pkg
            )
            self.cache_store_package(obj)

        if created:
            if not self.options['quiet']:
                sys.stdout.write('+ [p] %s/%s\n' % (cat, pkg))

        # Set all versions dead, then set found versions alive and
        # delete old versions
        if not self.options['all']:
            Version.objects.filter(
                package=obj,
                packaged=True
            ).update(alive=False)

        return obj

    def store_version(self, package, cpv, slot, overlay):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)

        overlays = self.overlays()

        if overlay in overlays:
            overlay = overlays[overlay]
        else:
            overlay = 'gentoo'

        created = False
        obj = self.cache_get_version(
            package.category, package.name, ver, rev, slot, overlay
        )
        if not obj:
            obj, created = Version.objects.get_or_create(
                package=package, slot=slot,
                revision=rev, version=ver,
                overlay=overlay,
                defaults={"alive": True, "packaged": True}
            )
        if not created: # Created objects have defaults values
            obj.alive = True
            obj.packaged = True
            obj.save()

        if created:
            self.cache_store_version(obj)

        # nothing to do (note: it can't be an upstream version because
        # overlay can't be empty here)
        if not created:
            return

        if not self.options['quiet']:
            sys.stdout.write('+ [v] %s \n' % (obj))

        if overlay == 'gentoo':
            package.n_packaged += 1
        else:
            package.n_overlay += 1
        package.n_versions += 1
        package.save()

        if self.options['no-log']:
            return

        VersionLog.objects.create(
            package=obj.package,
            action=VersionLog.VERSION_ADDED,
            slot=obj.slot,
            revision=obj.revision,
            version=obj.version,
            overlay=obj.overlay
        )

@commit_on_success
def purge_versions(options):
    # For each dead versions
    for version in Version.objects.filter(packaged=True, alive=False):
        if version.overlay == 'gentoo':
            version.package.n_packaged -= 1
        else:
            version.package.n_overlay -= 1
        version.package.n_versions -= 1
        version.package.save()

        if not options['quiet']:
            sys.stdout.write('- [v] %s\n' % (version))

        if options['no-log']:
            continue

        VersionLog.objects.create(
            package=version.package,
            action=VersionLog.VERSION_REMOVED,
            slot=version.slot,
            revision=version.revision,
            version=version.version,
            overlay=version.overlay
        )

    Version.objects.filter(packaged=True, alive=False).delete()


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Scan all packages'),
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
        make_option('--no-log',
            action='store_true',
            dest='no-log',
            default=False,
            help='Don\'t store logs'),
        make_option('--prefetch',
            action='store_true',
            dest='prefetch',
            default=False,
            help=('Prefetch all versions and packages from DB to '
                  'speedup full scan process.')),
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
        )
    args = '[package package ...]'
    help = 'Scans portage tree and fills database'

    def handle(self, *args, **options):
        scan_portage = ScanPortage(stdout=self.stdout, **options)

        if not options['quiet']:
            self.stdout.write('Scanning portage tree...\n')

        if options['prefetch']:
            if not options['quiet']:
                self.stdout.write('Prefetching objects...')
                self.stdout.flush()
            for package in Package.objects.all():
                scan_portage.cache_store_package(package)
            for version in Version.objects.select_related('package').all():
                scan_portage.cache_store_version(version)
            if not options['quiet']:
                self.stdout.write('done\n')

        if options['all']:
            scan_portage.run()
        elif len(args):
            for package in args:
                scan_portage.run(package)
        else:
            for package in sys.stdin.readlines():
                scan_portage.run(package[:-1])

        if options['purge-versions']:
            purge_versions(options)

        if not options['quiet']:
            self.stdout.write('Done.\n')
