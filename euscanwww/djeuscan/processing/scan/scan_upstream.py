import portage

from django.utils import timezone
from django.db.transaction import commit_on_success

from euscan import CONFIG, output
from euscan.scan import scan_upstream as euscan_scan_upstream

from djeuscan.processing import FakeLogger
from djeuscan.models import Package, Version, EuscanResult, VersionLog


class ScanUpstream(object):
    def __init__(self, logger=None, purge_versions=False):
        self.logger = logger or FakeLogger()
        self.purge_versions = purge_versions

    def scan(self, package):
        CONFIG["format"] = "dict"
        output.clean()
        output.set_query(package)

        euscan_scan_upstream(package)

        out = output.get_formatted_output()
        out_json = output.get_formatted_output("json")

        try:
            cpv = out[package]["metadata"]["cpv"]
            scan_time = out[package]["metadata"]["scan_time"]
            ebuild = out[package]["metadata"]["ebuild"]
        except KeyError:
            self.logger.error(
                "Error while scanning upstream for package %s!",
                package
            )
            self.logger.info(
                "Error %s",
                out_json
            )
            return {}

        obj = self.store_package(cpv)

        for res in out[package]["result"]:
            self.store_version(
                obj,
                res["version"],
                " ".join(res["urls"]),
                res["type"],
                res["handler"],
                res["confidence"],
            )

        self.store_result(obj, out_json, scan_time, ebuild)

    def store_result(self, package, formatted_log, scan_time, ebuild):
        # Remove previous logs
        EuscanResult.objects.filter(package=package).delete()

        obj = EuscanResult()
        obj.package = package
        obj.result = formatted_log
        obj.datetime = timezone.now()
        obj.scan_time = scan_time
        obj.ebuild = ebuild
        obj.save()

    def store_package(self, cpv):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)

        obj, created = Package.objects.get_or_create(category=cat, name=pkg)

        if created:
            self.logger.info('+ [p] %s/%s' % (cat, pkg))

        # Set all versions dead, then set found versions alive and
        # delete old versions
        if self.purge_versions:
            Version.objects.filter(
                package=obj, packaged=False
            ).update(alive=False)

        return obj

    def store_version(self, package, ver, url, version_type, handler,
                      confidence):
        obj, created = Version.objects.get_or_create(
            package=package,
            slot='',
            revision='r0',
            version=ver,
            overlay='',
            defaults={"alive": True, "urls": url, "packaged": False,
                      "vtype": version_type, "handler": handler,
                      "confidence": confidence}
        )
        if not created:
            obj.alive = True
            obj.urls = url
            obj.packaged = False
            obj.save()

        # If it's not a new version, just update the object and continue
        if not created:
            return

        self.logger.info('+ [u] %s %s' % (obj, url))

        VersionLog.objects.create(
            package=package,
            action=VersionLog.VERSION_ADDED,
            slot='',
            revision='r0',
            version=ver,
            overlay='',
            vtype=version_type,
        )

        package.n_versions += 1
        package.save()

    def purge_old_versions(self):
        if not self.purge_versions:
            return

        versions = Version.objects.filter(packaged=False, alive=False)
        for version in versions:
            VersionLog.objects.create(
                package=version.package,
                action=VersionLog.VERSION_REMOVED,
                slot=version.slot,
                revision=version.revision,
                version=version.version,
                overlay=version.overlay,
                vtype=version.vtype,
            )

            version.package.n_versions -= 1
            version.package.save()

            self.logger.info('- [u] %s %s' % (version, version.urls))

        versions.delete()


@commit_on_success
def scan_upstream(packages=None, purge_versions=False,
                  logger=None):
    logger = logger or FakeLogger()

    scan_handler = ScanUpstream(logger=logger, purge_versions=purge_versions)

    logger.info('Scanning upstream...')

    if not packages:
        packages = Package.objects.all()

    for pkg in packages:
        try:
            package = '%s/%s' % (pkg.category, pkg.name)
        except AttributeError:
            package = pkg

        logger.info('Scanning %s' % package)
        scan_handler.scan(package)

    scan_handler.purge_old_versions()

    logger.info('Done.')
