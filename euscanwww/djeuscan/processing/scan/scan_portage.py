import subprocess
from os.path import join

from portage import catpkgsplit, catsplit
from portage.dbapi import porttree

from xml.etree.ElementTree import iterparse, ParseError

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
        self.portdbapi = porttree.portdbapi()

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
        if query:
            cmd.extend(['--exact', query])
        if category:
            cmd.extend(['-C', category])

        sub = subprocess.Popen(cmd, stdout=subprocess.PIPE)
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
                    package["versions"].append((cpv, slot, overlay))

            elif event == "end":  # on tag closing
                if elem.tag == "package":
                    # clean old data
                    yield package
                    package = {"versions": []}

                if elem.tag == "category":
                    # clean old data
                    category = ""
            elem.clear()

    def prepare_purge_versions(self, packages, query=None, category=None):
        if not self.purge_versions:
            return

        # Set all versions dead, then set found versions alive and
        # delete old versions
        if not query:
            # Optimisation for --all or --category
            self.logger.info('Killing existing versions...')
            qs = Version.objects.filter(packaged=True)
            if category:
                qs = qs.filter(package__category=category)
            qs.update(alive=False)
            self.logger.info('done')
        else:
            for package in packages:
                Version.objects.filter(package=package, packaged=True).\
                    update(alive=False)

    def scan(self, query=None, category=None):
        if not query:
            current_packages = Package.objects.all()
        elif '/' in query:
            cat, pkg = catsplit(query)
            current_packages = Package.objects.filter(category=cat, name=pkg)
        else:
            current_packages = Package.objects.filter(name=query)
        if category:
            current_packages = current_packages.filter(category=category)

        self.prepare_purge_versions(current_packages, query, category)

        packages_alive = set()

        for data in self.scan_eix_xml(query, category):
        #for data in self.scan_gentoopm(query, category):
            cat, pkg = data['category'], data['package']
            package = self.store_package(
                cat, pkg, data['homepage'], data['description']
            )
            packages_alive.add("%s/%s" % (cat, pkg))
            for cpv, slot, overlay in data['versions']:
                self.store_version(package, cpv, slot, overlay)

        self.purge_old_packages(current_packages, packages_alive)
        self.purge_old_versions()

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

    def store_version(self, package, cpv, slot, overlay):
        cat, pkg, ver, rev = catpkgsplit(cpv)
        if not overlay:
            overlay = 'gentoo'

        created = False
        obj = self.cache_get_version(
            package.category, package.name, ver, rev, slot, overlay
        )

        overlay_path = self.portdbapi.getRepositoryPath(overlay)
        package_path = join(overlay_path, package.category, package.name)
        ebuild_path = join(package_path, "%s.ebuild" % cpv.split("/")[-1])
        metadata_path = join(package_path, "metadata.xml")

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
                    "handler": "portage",
                    "ebuild_path": ebuild_path,
                    "metadata_path": metadata_path,
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

    def purge_old_packages(self, packages, alive):
        if not self.purge_packages:
            return

        for package in packages:
            cp = "%s/%s" % (package.category, package.name)
            if cp not in alive:
                self.logger.info('- [p] %s' % (package))
                package.delete()

    def purge_old_versions(self):
        if not self.purge_versions:
            return

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

        versions.delete()


@commit_on_success
def scan_portage(packages=None, category=None, no_log=False,
                 purge_packages=False, purge_versions=False, prefetch=False,
                 logger=None):

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
        scan_handler.scan(category=category)
    else:
        for pkg in packages:
            if isinstance(pkg, Package):
                scan_handler.scan('%s/%s' % (pkg.category, pkg.name))
            else:
                scan_handler.scan(pkg)

    logger.info('Done.')
