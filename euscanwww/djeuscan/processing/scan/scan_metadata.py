import os

import portage
from gentoolkit.metadata import MetaData

import xml.etree.cElementTree as etree

from django.db.transaction import commit_on_success
from django.core.management.color import color_style
from django.core.exceptions import ValidationError

from djeuscan.models import Package, Version, Herd, Maintainer
from djeuscan.processing import FakeLogger


class ScanMetadata(object):
    def __init__(self, logger=None):
        self.style = color_style()
        self.logger = logger or FakeLogger()

    def get_package(self, query):
        try:
            return Package.objects.get(name=query)
        except Package.DoesNotExist:
            pass

        try:
            category, package = portage.catsplit(query)
            return Package.objects.get(category=category, name=package)
        except Package.DoesNotExist:
            pass

        try:
            category, package, ver, rev = portage.catpkgsplit(query)
            return Package.objects.get(category=category, name=package)
        except Package.DoesNotExist:
            pass

        return None

    def metadata_from_db(self, query, pkg=None):
        if not pkg:
            pkg = self.get_package(query)

        try:
            version = Version.objects.filter(package=pkg).\
                values('metadata_path').order_by('version', 'revision')[0]
        except IndexError:
            return pkg, None

        if not version['metadata_path']:
            return pkg, None
        return pkg, MetaData(version['metadata_path'])

    def metadata_from_portage(self, query, pkg=None):
        from gentoolkit.query import Query

        matches = Query(query).smart_find(
                in_installed=True,
                in_porttree=True,
                in_overlay=True,
                include_masked=True,
                show_progress=False,
                no_matches_fatal=False,
        )

        if not matches:
            self.logger.error(
                self.style.ERROR("Unknown package '%s'" % query)
            )
            return pkg, None

        matches = sorted(matches)
        package = matches.pop()
        if '9999' in package.version and len(matches):
            package = matches.pop()

        if not pkg:
            pkg, created = Package.objects.get_or_create(
                category=package.category, name=package.name
            )
        else:
            created = False

        if created:
            self.logger.info('+ [p] %s/%s' % (pkg.category, pkg.name))

        return pkg, package.metadata

    def scan(self, query=None, pkg=None):
        try:
            metadata = None
            pkg, metadata = self.metadata_from_db(query, pkg)

            if not metadata:
                pkg, metadata = self.metadata_from_portage(query, pkg)

            if not metadata:
                return
        except Exception as e:
            if pkg:
                self.logger.error(
                    self.style.ERROR('%s/%s: %s' %
                                     (pkg.category, pkg.name, str(e)))
                )
            else:
                self.logger.error(
                    self.style.ERROR('%s: %s' % (query, str(e)))
                )
            return

        herds = dict(
            [(herd[0], herd) for herd in metadata.herds(True)]
        )
        maintainers = dict(
            [(m.email, m) for m in metadata.maintainers()]
        )

        existing_herds = [h.herd for h in pkg.herds.all()]
        new_herds = set(herds.keys()).difference(existing_herds)
        old_herds = set(existing_herds).difference(herds.keys())

        existing_maintainers = [m.email for m in pkg.maintainers.all()]
        new_maintainers = set(maintainers.keys()).\
                          difference(existing_maintainers)
        old_maintainers = set(existing_maintainers).\
                          difference(maintainers.keys())

        for herd in pkg.herds.all():
            if herd.herd in old_herds:
                pkg.herds.remove(herd)

        for herd in new_herds:
            herd = self.store_herd(*herds[herd])
            pkg.herds.add(herd)

        for maintainer in pkg.maintainers.all():
            email = maintainer.email
            name = maintainer.name
            if email in old_maintainers:
                pkg.maintainers.remove(maintainer)
            if (email in maintainers and
                email == name and
                maintainers[email].name != name and
                maintainers[email].name):
                maintainer.name = maintainers[email].name
                maintainer.save()

        for maintainer in new_maintainers:
            maintainer = maintainers[maintainer]
            try:
                maintainer = self.store_maintainer(
                    maintainer.name, maintainer.email
                    )
                pkg.maintainers.add(maintainer)
            except ValidationError:
                self.logger.error(
                    self.style.ERROR("Bad maintainer: '%s' '%s'" % \
                                         (maintainer.name, maintainer.email))
                )

        pkg.save()

    def store_herd(self, name, email):
        if not name:
            name = '{nil}'
        name = name.strip("\r").strip("\n").strip("\t").strip()

        herd, created = Herd.objects.get_or_create(
            herd=name,
            defaults={"email": email}
        )

        if created:
            self.logger.info('+ [h] %s <%s>' % (name, email))

        herd.email = email
        herd.save()

        return herd

    def store_maintainer(self, name, email):
        if not name:
            name = email
        if not name:
            name = '{nil}'

        maintainer, created = Maintainer.objects.get_or_create(
            email=email,
            defaults={"name": name}
        )

        if created:
            self.logger.info(
                '+ [m] %s <%s>' % (name.encode('utf-8'), email)
            )
        return maintainer

    def populate_herds_and_maintainers(self, herds_xml_path=None):
        self.logger.info("Populating herds and maintainers from herds.xml...")

        herds_xml_path = herds_xml_path or os.path.join(
            portage.settings["PORTDIR"], "metadata", "herds.xml"
        )
        try:
            self._herdstree = etree.parse(herds_xml_path)
        except IOError:
            return None

        for herd_node in self._herdstree.getiterator('herd'):
            herd_name = herd_node.findtext('name')
            herd_email = herd_node.findtext('email')

            try:
                herd = self.store_herd(herd_name, herd_email)
            except ValidationError:  # just skip invalid data
                continue

            herd.maintainers.clear()  # clear previous data

            for maintainer_node in herd_node:
                if maintainer_node.tag == "maintainer":
                    maintainer_name = maintainer_node.findtext('name')
                    maintainer_email = maintainer_node.findtext('email')

                    try:
                        maintainer = self.store_maintainer(
                            maintainer_name, maintainer_email
                        )
                    except ValidationError:
                        self.logger.error(
                            self.style.ERROR("Bad maintainer: '%s' '%s'" % \
                                             (maintainer_name, maintainer_email))
                            )

                    herd.maintainers.add(maintainer)


@commit_on_success
def scan_metadata(packages=None, category=None, logger=None, populate=False):
    scan_handler = ScanMetadata(logger=logger)

    if category:
        packages = Package.objects.filter(category=category)
    elif packages is None:
        packages = Package.objects.all()

    if populate:
        scan_handler.populate_herds_and_maintainers()

    for pkg in packages:
        if isinstance(pkg, Package):
            scan_handler.scan('%s/%s' % (pkg.category, pkg.name), pkg)
        else:
            scan_handler.scan(pkg)
