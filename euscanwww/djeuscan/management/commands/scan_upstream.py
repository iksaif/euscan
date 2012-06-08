import portage
import sys
import re

from optparse import make_option

from django.utils import timezone
from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand

from euscan import CONFIG, output
from euscan.scan import scan_upstream

from djeuscan.models import Package, Version, EuscanResult, VersionLog


class ScanUpstream(object):
    def __init__(self, quiet=False):
        self.quiet = quiet

    def scan(self, package):
        CONFIG["format"] = "dict"
        output.set_query(package)

        scan_upstream(package)

        out = output.get_formatted_output()
        out_json = output.get_formatted_output("json")

        try:
            cpv = out[package]["metadata"]["cpv"]
        except KeyError:
            return {}

        obj = self.store_package(cpv)

        for res in out[package]["result"]:
            self.store_version(obj, res["version"], " ".join(res["urls"]))

        self.store_result(obj, out_json)

        return out

    def store_result(self, package, log):
        # Remove previous logs
        EuscanResult.objects.filter(package=package).delete()

        obj = EuscanResult()
        obj.package = package
        obj.result = log
        obj.datetime = timezone.now()
        obj.save()

    def store_package(self, cpv):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)

        obj, created = Package.objects.get_or_create(category=cat, name=pkg)

        if created and not self.quiet:
            sys.stdout.write('+ [p] %s/%s\n' % (cat, pkg))

        # Set all versions dead, then set found versions alive and
        # delete old versions
        Version.objects.filter(package=obj, packaged=False).update(alive=False)

        return obj

    def store_version(self, package, ver, url):
        obj, created = Version.objects.get_or_create(
            package=package, slot='', revision='r0', version=ver, overlay='',
            defaults={"alive": True, "urls": url, "packaged": True}
        )
        if not created:
            obj.alive = True
            obj.urls = url
            obj.packaged = False
            obj.save()

        # If it's not a new version, just update the object and continue
        if not created:
            return

        if not self.quiet:
            sys.stdout.write('+ [u] %s %s\n' % (obj, url))

        VersionLog.objects.create(
            package=package,
            action=VersionLog.VERSION_ADDED,
            slot='',
            revision='r0',
            version=ver,
            overlay=''
        )

        package.n_versions += 1
        package.save()

    @commit_on_success
    def parse_output(self, output):
        from portage.versions import _cp

        package_re = re.compile(
            r'^ \* (?P<cpv>' + _cp + ') \[(?P<overlay>.*?)\]$'
        )
        version_re = re.compile(
            r'^Upstream Version: (?P<ver>.*?) (?P<url>.*?)$'
        )

        package = None
        log = ""

        while True:
            line = output.readline()
            if line == '':
                break
            match = package_re.match(line)
            if match:
                if package:
                    self.store_result(package, log)

                cpv = match.group('cpv')
                package = self.store_package(cpv)
                log = line
                continue

            log += line

            match = version_re.match(line)
            if match:
                ver = match.group('ver')
                url = match.group('url')
                self.store_version(package, ver, url)

        if package:
            self.store_result(package, log)


@commit_on_success
def purge_versions(quiet=False):
    # For each dead versions
    for version in Version.objects.filter(packaged=False, alive=False):
        VersionLog.objects.create(
            package=version.package,
            action=VersionLog.VERSION_REMOVED,
            slot=version.slot,
            revision=version.revision,
            version=version.version,
            overlay=version.overlay
        )

        version.package.n_versions -= 1
        version.package.save()

        if not quiet:
            sys.stdout.write('- [u] %s %s\n' % (version, version.urls))
    Version.objects.filter(packaged=False, alive=False).delete()


class Command(BaseCommand):
    _overlays = {}

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Scan all packages'),
        make_option('--feed',
            action='store_true',
            dest='feed',
            default=False,
            help='Read euscan output from stdin'),
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
        scan_upstream = ScanUpstream(options["quiet"])

        if options['feed']:
            scan_upstream.parse_output(sys.stdin)
            if options['purge-versions']:
                purge_versions(options["quiet"])
            return

        if not options['quiet']:
            self.stdout.write('Scanning upstream...\n')

        if options['all']:
            for pkg in Package.objects.all():
                scan_upstream.scan('%s/%s' % (pkg.category, pkg.name))
        elif args:
            for arg in args:
                scan_upstream.scan(arg)
        else:
            for package in sys.stdin.readlines():
                scan_upstream.scan(package[:-1])

        if options['purge-versions']:
            purge_versions(options["quiet"])

        if not options['quiet']:
            self.stdout.write('Done.\n')
