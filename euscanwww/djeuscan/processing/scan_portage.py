import subprocess
import portage
import os
import re

from xml.dom.minidom import parseString

from django.db.transaction import commit_on_success
from django.core.management.color import color_style

from euscan.helpers import get_version_type

from djeuscan.processing import FakeLogger
from djeuscan.models import Package, Version, VersionLog


class ScanPortage(object):
    def __init__(self, logger=None, no_log=False, purge_packages=False,
                 purge_versions=False):
        self.logger = logger or FakeLogger()
        self.no_log = no_log
        self.purge_packages = purge_packages
        self.purge_versions = purge_versions

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

    def scan(self, query=None):
        cmd = ['eix', '--xml']
        if query:
            cmd.extend(['--exact', query])

        if not query:
            current_packages = Package.objects.all()
        elif '/' in query:
            cat, pkg = portage.catsplit(query)
            current_packages = Package.objects.filter(category=cat, name=pkg)
        else:
            current_packages = Package.objects.filter(name=query)

        if self.purge_versions:
            if not query:
                self.logger.info('Killing existing versions...')
                Version.objects.filter(packaged=True).update(alive=False)
                self.logger.info('done')
            else:
                for package in current_packages:
                    Version.objects.filter(package=package, packaged=True).update(alive=False)

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE).\
            communicate()[0]

        if len(output) == 0 and query:
            self.logger.error(
                self.style.ERROR(
                    "Unknown package '%s'" % query
                    )
                )
            return

        packages_alive = set()

        dom = parseString(output)
        # SAX
        for category_tag in dom.getElementsByTagName("category"):
            for package_tag in category_tag.getElementsByTagName("package"):
                cat = category_tag.getAttribute("name")
                pkg = package_tag.getAttribute("name")
                homepage_tags = package_tag.getElementsByTagName("homepage")
                try:
                    homepage = homepage_tags[0].firstChild.nodeValue
                except (IndexError, AttributeError):
                    homepage = ""
                desc_tags = package_tag.getElementsByTagName("description")
                try:
                    desc = desc_tags[0].firstChild.nodeValue
                except (IndexError, AttributeError):
                    desc = ""

                package = self.store_package(cat, pkg, homepage, desc)
                packages_alive.add('%s/%s' % (cat, pkg))

                for version_tag in package_tag.\
                        getElementsByTagName("version"):
                    cpv = "%s/%s-%s" % (cat, pkg,
                                        version_tag.getAttribute("id"))
                    slot = version_tag.getAttribute("slot")
                    overlay = version_tag.getAttribute("repository")
                    self.store_version(package, cpv, slot, overlay)

        if self.purge_packages:
            for package in current_packages:
                cp = "%s/%s" % (package.category, package.name)
                if cp not in packages_alive:
                    self.logger.info('- [p] %s' % (package))
                    package.delete()
        if self.purge_versions:
            self.purge_old_versions(current_packages)

    def store_package(self, cat, pkg, homepage, description):
        created = False
        obj = self.cache_get_package(cat, pkg)

        if not obj:
            obj, created = Package.objects.get_or_create(
                category=cat,
                name=pkg,
                homepage=homepage,
                description=description,
            )
            self.cache_store_package(obj)

        if created:
            self.logger.info('+ [p] %s/%s' % (cat, pkg))

        # Set all versions dead, then set found versions alive and
        # delete old versions
        if not self.purge_versions:
            Version.objects.filter(
                package=obj,
                packaged=True
            ).update(alive=False)

        return obj

    def store_version(self, package, cpv, slot, overlay):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)
        if not overlay:
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
                defaults={
                    "alive": True,
                    "packaged": True,
                    "version_type": get_version_type(ver),
                    "confidence": 100,
                    "handler": "portage"
                }
            )
        if not created:  # Created objects have defaults values
            obj.alive = True
            obj.packaged = True
            obj.save()

        if created:
            self.cache_store_version(obj)

        # nothing to do (note: it can't be an upstream version because
        # overlay can't be empty here)
        if not created:
            return

        self.logger.info('+ [v] %s' % (obj))

        if overlay == 'gentoo':
            package.n_packaged += 1
        else:
            package.n_overlay += 1
        package.n_versions += 1
        package.save()

        if self.no_log:
            return

        VersionLog.objects.create(
            package=obj.package,
            action=VersionLog.VERSION_ADDED,
            slot=obj.slot,
            revision=obj.revision,
            version=obj.version,
            overlay=obj.overlay
        )

    def purge_old_versions(self, packages):
        # For each dead versions
        if packages:
            versions = []
            for package in packages:
                qs = Version.objects.filter(package=package, packaged=True, alive=False)
                for version in qs:
                    versions.append(version)
        else:
            versions = Version.objects.filter(packaged=True, alive=False)

        for version in versions:
            if version.overlay == 'gentoo':
                version.package.n_packaged -= 1
            else:
                version.package.n_overlay -= 1
            version.package.n_versions -= 1
            version.package.save()

            self.logger.info('- [v] %s' % (version))

            if self.no_log:
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

@commit_on_success
def scan_portage(packages=None, no_log=False, purge_packages=False,
                 purge_versions=False, prefetch=False, logger=None):

    logger = logger or FakeLogger()

    if packages is None:
        prefetch = True

    scan_handler = ScanPortage(
        logger=logger,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
    )

    logger.info('Scanning portage tree...')

    if prefetch:
        logger.info('Prefetching objects...')
        for package in Package.objects.all():
            scan_handler.cache_store_package(package)
        for version in Version.objects.select_related('package').all():
            scan_handler.cache_store_version(version)
        logger.info('done')

    if not packages:
        scan_handler.scan()
    else:
        for pkg in packages:
            if isinstance(pkg, Package):
                scan_handler.scan('%s/%s' % (pkg.category, pkg.name))
            else:
                scan_handler.scan(pkg)

    logger.info('Done.')
    return True
