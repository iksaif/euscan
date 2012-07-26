import os

from gentoolkit.query import Query
from gentoolkit.dbapi import PORTDB

import xml.etree.cElementTree as etree

from django.db.transaction import commit_on_success
from django.core.management.color import color_style
from django.core.exceptions import ValidationError

from djeuscan.models import Package, Herd, Maintainer
from djeuscan.processing import FakeLogger


class ScanMetadata(object):
    def __init__(self, logger=None):
        self.style = color_style()
        self.logger = logger or FakeLogger()

    def scan(self, query=None, obj=None):
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
            return

        matches = sorted(matches)
        pkg = matches.pop()
        if '9999' in pkg.version and len(matches):
            pkg = matches.pop()

        if not obj:
            obj, created = Package.objects.get_or_create(
                category=pkg.category, name=pkg.name
            )
        else:
            created = False

        if created:
            self.logger.info('+ [p] %s/%s' % (pkg.category, pkg.name))

        try:
            if not pkg.metadata:
                return
        except Exception as e:
            self.logger.error(
                self.style.ERROR('%s/%s: %s' % (pkg.category, pkg.name, str(e)))
            )
            return

        herds = dict(
            [(herd[0], herd) for herd in pkg.metadata.herds(True)]
        )
        maintainers = dict(
            [(m.email, m) for m in pkg.metadata.maintainers()]
        )

        existing_herds = [h.herd for h in obj.herds.all()]
        new_herds = set(herds.keys()).difference(existing_herds)
        old_herds = set(existing_herds).difference(herds.keys())

        existing_maintainers = [m.email for m in obj.maintainers.all()]
        new_maintainers = set(maintainers.keys()).\
                          difference(existing_maintainers)
        old_maintainers = set(existing_maintainers).\
                          difference(maintainers.keys())

        for herd in obj.herds.all():
            if herd.herd in old_herds:
                obj.herds.remove(herd)

        for herd in new_herds:
            herd = self.store_herd(*herds[herd])
            obj.herds.add(herd)

        for maintainer in obj.maintainers.all():
            if maintainer.email in old_maintainers:
                obj.maintainers.remove(maintainer)

        for maintainer in new_maintainers:
            maintainer = maintainers[maintainer]
            try:
                maintainer = self.store_maintainer(
                    maintainer.name, maintainer.email
                    )
                obj.maintainers.add(maintainer)
            except ValidationError:
                self.logger.error(
                    self.style.ERROR("Bad maintainer: '%s' '%s'" % \
                                         (maintainer.name, maintainer.email))
                )
        obj.save()

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
            PORTDB.settings["PORTDIR"], "metadata", "herds.xml"
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

                    maintainer = self.store_maintainer(
                        maintainer_name, maintainer_email
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
