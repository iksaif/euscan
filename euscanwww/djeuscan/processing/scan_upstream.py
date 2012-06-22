import portage
import sys

from django.utils import timezone
from django.db.transaction import commit_on_success

from euscan import CONFIG, output
from euscan.scan import scan_upstream as euscan_scan_upstream

from djeuscan.models import Package, Version, EuscanResult, VersionLog


class ScanUpstream(object):
    def __init__(self, quiet=False):
        self.quiet = quiet

    def scan(self, package):
        CONFIG["format"] = "dict"
        output.set_query(package)

        euscan_scan_upstream(package)

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
            defaults={"alive": True, "urls": url, "packaged": False}
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


def scan_upstream(packages=None, purge_versions=False, quiet=False,
                  logger=None, stdout=None):

    stdout = sys.stdout if stdout is None else stdout

    scan_handler = ScanUpstream(quiet)

    if not quiet:
        stdout.write('Scanning upstream...\n')

    if packages is None:
        packages = Package.objects.all()

    for pkg in packages:
        if isinstance(pkg, Package):
            scan_handler.scan('%s/%s' % (pkg.category, pkg.name))
        else:
            scan_handler.scan(pkg)

    if purge_versions:
        purge_versions(quiet)

    if not quiet:
        stdout.write('Done.\n')
