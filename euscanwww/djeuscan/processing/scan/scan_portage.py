import subprocess

import os
from os.path import join

import portage

from xml.etree.ElementTree import iterparse, ParseError

from django.db.transaction import commit_on_success
from django.db import models
from django.core.management.color import color_style

from euscan.version import get_version_type

from djeuscan.processing import FakeLogger
from djeuscan.models import Package, Version, VersionLog, Category, Overlay


class ScanPortage(object):
    def __init__(self, logger=None, no_log=False, purge_packages=False,
                 purge_versions=False, upstream=False):
        self.logger = logger or FakeLogger()
        self.no_log = no_log
        self.purge_packages = purge_packages
        self.purge_versions = purge_versions
        self.upstream = upstream

        self.style = color_style()

        self._cache = {'packages': {}, 'versions': {}}
        self._overlays = None
        self._packages_updated = set()
        self._versions = set()
        self._versions_seen = set()

    def packages_updated(self):
        return list(self._packages_updated)

    def hash_package(self, category, name):
        return '%s/%s' % (category, name)

    def cache_store_package(self, package):
        key = self.hash_package(package.category, package.name)
        self._cache['packages'][key] = package

    def cache_get_package(self, category, name):
        return self._cache['packages'].get(
            self.hash_package(category, name)
        )

    def hash_version(self, category, name, version, revision,
                           overlay):
        key = '%s/%s-%s-r%s %s' % (category, name,
                                   version, revision,
                                   overlay)
        return key

    def cache_get_version(self, category, name, version, revision,
                          overlay):
        key = self.hash_version(category, name, version, revision,
                                      overlay)
        return self._cache['versions'].get(key)

    def cache_store_version(self, version):
        key = self.hash_version(
            version.package.category, version.package.name, version.version,
            version.revision, version.overlay
        )
        self._cache['versions'][key] = version
        self._versions.add(version)

    def scan_gentoopm(self, query, category=None):
        import gentoopm

        pm = gentoopm.get_package_manager()

        if category:
            packages = pm.stack.filter(key_category=category)
        elif query:
            packages = pm.stack.filter(query)
        else:
            packages = pm.stack

        package = {}
        package_name = None

        for p in packages:
            pkg = p.key.package

            if pkg != package_name:
                if package_name:
                    yield package
                package_name = pkg
                package['package'] = p.key.package
                package['category'] = p.key.category
                package['homepage'] = ' '.join(p.homepages)
                package['description'] = p.description
                package['versions'] = []
            package['versions'].append(
                (p._cpv, p.slot, p.repository or 'gentoo')
            )

        if package_name:
            yield package

    def scan_eix_xml(self, query, category=None):
        cmd = ['eix', '--xml']
        env = os.environ
        env['XML_OVERLAY'] = 'true'
        if query:
            cmd.extend(['--exact', query])
        if category:
            cmd.extend(['-C', category])

        sub = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
        output = sub.stdout

        try:
            parser = iterparse(output, ["start", "end"])
            parser.next()  # read root tag just for testing output
        except ParseError:
            if query:
                msg = "Unknown package '%s'" % query
            else:
                msg = "No packages."
            self.logger.error(self.style.ERROR(msg))
            return

        package = {'versions': []}
        category = ""

        for event, elem in parser:
            if event == "start":  # on tag opening
                if elem.tag == "category":
                    category = elem.attrib["name"]
                elif elem.tag == "package":
                    package["package"] = elem.attrib["name"]
                    package["category"] = category
                elif elem.tag in ["description", "homepage"]:
                    package[elem.tag] = elem.text or ""
                elif elem.tag == "version":
                    # append version data to versions
                    cpv = "%s/%s-%s" % (
                        package["category"],
                        package["package"],
                        elem.attrib["id"]
                    )
                    slot = elem.attrib.get("slot", "0")
                    overlay = elem.attrib.get("repository", "gentoo")
                    overlay_path = elem.attrib.get("overlay", None)
                    package["versions"].append(
                        (cpv, slot, overlay, overlay_path)
                    )

            elif event == "end":  # on tag closing
                if elem.tag == "package":
                    # clean old data
                    yield package
                    package = {"versions": []}

                if elem.tag == "category":
                    # clean old data
                    category = ""
            elem.clear()

    def scan(self, query=None, category=None):
        for data in self.scan_eix_xml(query, category):
        #for data in self.scan_gentoopm(query, category):
            cat, pkg = data['category'], data['package']
            package = self.store_package(
                cat, pkg, data['homepage'], data['description']
            )

            new_version = False
            for cpv, slot, overlay, overlay_path in data['versions']:
                obj, created = self.store_version(
                    package, cpv, slot, overlay, overlay_path
                )
                self._versions_seen.add(obj)
                new_version = created or new_version

            # If the package has at least one new version scan upstream for it
            if new_version:
                self._packages_updated.add(package)

        self.purge_old_versions()
        self.purge_old_packages()

    def store_package(self, cat, pkg, homepage, description):
        created = False
        obj = self.cache_get_package(cat, pkg)

        if not obj:
            obj, created = Package.objects.get_or_create(
                category=cat,
                name=pkg,
                defaults={"homepage": homepage, "description": description},
            )
            self.cache_store_package(obj)

        if created:
            self.logger.info('+ [p] %s/%s' % (cat, pkg))

        return obj

    def store_version(self, package, cpv, slot, overlay, overlay_path):
        cat, pkg, ver, rev = portage.catpkgsplit(cpv)
        if not overlay:
            overlay = 'gentoo'

        created = False
        obj = self.cache_get_version(
            package.category, package.name, ver, rev, overlay
        )

        overlay_path = overlay_path or portage.settings["PORTDIR"]
        package_path = join(overlay_path, package.category, package.name)
        ebuild_path = join(package_path, "%s.ebuild" % cpv.split("/")[-1])
        metadata_path = join(package_path, "metadata.xml")

        if not obj:
            obj, created = Version.objects.get_or_create(
                package=package,
                revision=rev,
                version=ver,
                overlay=overlay,
                defaults={
                    "slot": slot,
                    "packaged": True,
                    "vtype": get_version_type(ver),
                    "confidence": 100,
                    "handler": "portage",
                    "ebuild_path": ebuild_path,
                    "metadata_path": metadata_path,
                }
            )
        if not created:  # Created objects have defaults values
            if obj.slot != slot or obj.package != True:
                obj.slot = slot
                obj.packaged = True
                obj.save()

        if created:
            self.cache_store_version(obj)

        # nothing to do (note: it can't be an upstream version because
        # overlay can't be empty here)
        if not created:
            return obj, created

        # New version created
        self.logger.info('+ [v] %s' % (obj))

        if overlay == 'gentoo':
            package.n_packaged += 1
        else:
            package.n_overlay += 1
        package.n_versions += 1
        package.save()

        if not self.no_log:
            VersionLog.objects.create(
                package=obj.package,
                action=VersionLog.VERSION_ADDED,
                slot=obj.slot,
                revision=obj.revision,
                version=obj.version,
                overlay=obj.overlay,
                vtype=obj.vtype,
            )

        return obj, created

    def purge_old_packages(self):
        if not self.purge_packages:
            return

        packages = (
            Package.objects.values("id")
                           .annotate(version_count=models.Count("version"))
                           .filter(version_count=0)
        )
        packages = (
            Package.objects.filter(id__in=[package['id'] for package in packages])
        )

        for package in packages:
            self.logger.info('- [p] %s' % (package))
            package.delete()

    def version_hack(self, version):
        try:
            if version.package.last_version_gentoo:
                version.package.last_version_gentoo.pk
            if version.package.last_version_overlay:
                version.package.last_version_overlay.pk
            if version.package.last_version_upstream:
                version.package.last_version_upstream.pk
        except Version.DoesNotExist:
            version.package.last_version_gentoo = None
            version.package.last_version_overlay = None
            version.package.last_version_upstream = None

    def purge_old_versions(self):
        if not self.purge_versions:
            return

        versions = self._versions.difference(self._versions_seen)

        for version in versions:
            self.logger.info('- [v] %s' % (version))

            if version.packaged == False:
                continue # Not our job

            # Fix last_version_ stuff that is sometime broken
            self.version_hack(version)

            if version.overlay == 'gentoo':
                version.package.n_packaged -= 1
            else:
                version.package.n_overlay -= 1
            version.package.n_versions -= 1
            version.package.save()

            if self.no_log:
                continue

            VersionLog.objects.create(
                package=version.package,
                action=VersionLog.VERSION_REMOVED,
                slot=version.slot,
                revision=version.revision,
                version=version.version,
                overlay=version.overlay,
                vtype=version.vtype,
            )
            # remove from last version ?
            version.delete()

    def prefetch(self, packages, category):
        self.logger.info('Prefetching current objects...')

        ppackages = Package.objects.all()
        pversions = Version.objects.filter(packaged=True).select_related('package').all()

        if category:
            ppackages = ppackages.filter(category=category)
            pversions = pversions.filter(package__category=category)
        if packages:
            ids = [ package.id for package in packages ]
            ppackages = ppackages.filter(pk__in=ids)
            pversions = pversions.filter(package__pk__in=ids)

        for package in ppackages:
            self.cache_store_package(package)
        for version in pversions:
            self.cache_store_version(version)

        self.logger.info('done')

def populate_categories(logger):
    # Populate Category and Overlay
    # TODO: - use portage.settings.categories()
    #       - read metadata.xml to add description
    for cat in Package.objects.values('category').distinct():
        obj, created = Category.objects.get_or_create(name=cat["category"])
        if created:
            logger.info("+ [c] %s", cat["category"])

def populate_overlays(logger):
    # TODO: - get informations from layman and portage (path, url)
    for overlay in Version.objects.values('overlay').distinct():
        if not overlay["overlay"]:
            continue
        obj, created = Overlay.objects.get_or_create(name=overlay["overlay"])
        if created:
            logger.info("+ [o] %s", overlay["overlay"])


@commit_on_success
def scan_portage(packages=None, category=None, no_log=False, upstream=False,
                 purge_packages=False, purge_versions=False, logger=None):

    logger = logger or FakeLogger()

    scan_handler = ScanPortage(
        logger=logger,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions
    )

    logger.info('Scanning portage tree...')

    if not packages:
        qs = Package.objects.all()
        if category:
            qs = qs.filter(category=category)
        prefetch_packages = qs
    else:
        results = []
        for package in packages:
            if isinstance(package, Package):
                results.append(package)
            else:
                if '/' in package:
                    cat, pkg = portage.catsplit(package)
                    qs = Package.objects.filter(category=cat, name=pkg)
                else:
                    qs = Package.objects.filter(name=package)
                for package in qs:
                    results.append(package)
        prefetch_packages = results


    scan_handler.prefetch(prefetch_packages, category)

    if not packages and category:
        scan_handler.scan(category=category)
    elif not packages:
        scan_handler.scan()
    else:
        for pkg in packages:
            if isinstance(pkg, Package):
                scan_handler.scan('%s/%s' % (pkg.category, pkg.name))
            else:
                scan_handler.scan(pkg)

    populate_categories(logger)
    populate_overlays(logger)

    logger.info('Done.')
    return scan_handler.packages_updated()
