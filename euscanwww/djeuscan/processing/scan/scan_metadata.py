import os.path

from gentoolkit.query import Query
from gentoolkit.errors import GentoolkitFatalError

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

        if not pkg.metadata:
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
        new_maintainers = set(maintainers.keys()).difference(existing_maintainers)
        old_maintainers = set(existing_maintainers).difference(maintainers.keys())

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

@commit_on_success
def scan_metadata(packages=None, category=None, logger=None):
    scan_handler = ScanMetadata(logger=logger)

    if category:
        packages = Package.objects.filter(category=category)
    elif not packages:
        packages = Package.objects.all()

    for pkg in packages:
        if isinstance(pkg, Package):
            scan_handler.scan('%s/%s' % (pkg.category, pkg.name), pkg)
        else:
            scan_handler.scan(pkg)

