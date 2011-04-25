import datetime

from optparse import make_option

from django.db.models import Count, Sum
from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand, CommandError
from euscanwww.euscan.models import Package, HerdLog, MaintainerLog, CategoryLog, Herd, Maintainer, Version

class Command(BaseCommand):
    _overlays = {}
    help = 'Update counters'

    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
        )

    @commit_on_success
    def handle(self, *args, **options):
        now = datetime.datetime.now()

        categories = {}
        herds = {}
        maintainers = {}

        # Could be done using raw SQL queries, but I don't have time for that
        # right now ...

        for cat in Package.objects.values('category').distinct():
            clog = CategoryLog()
            clog.datetime = now
            clog.category = cat['category']
            categories[clog.category] = clog

        for herd in Herd.objects.all():
            hlog = HerdLog()
            hlog.datetime = now
            hlog.herd = herd
            herds[herd] = hlog

        for maintainer in Maintainer.objects.all():
            mlog = MaintainerLog()
            mlog.datetime = now
            mlog.maintainer = maintainer
            maintainers[maintainer] = mlog

        for package in Package.objects.all():
            # Should not be needed, but can't hurt
            package.n_versions = Version.objects.filter(package=package).count()
            package.n_packaged = Version.objects.filter(package=package, packaged=True, overlay='gentoo').count()
            package.n_overlay = Version.objects.filter(package=package, packaged=True).exclude(overlay='gentoo').count()
            package.save()

            for herd in package.herds.all():
                herds[herd].n_packages += 1
                herds[herd].n_versions += package.n_versions
                herds[herd].n_packaged += package.n_packaged
                herds[herd].n_overlay += package.n_overlay

            for maintainer in package.maintainers.all():
                maintainers[maintainer].n_packages += 1
                maintainers[maintainer].n_versions += package.n_versions
                maintainers[maintainer].n_packaged += package.n_packaged
                maintainers[maintainer].n_overlay += package.n_overlay

            categories[package.category].n_packages += 1
            categories[package.category].n_versions += package.n_versions
            categories[package.category].n_packaged += package.n_packaged
            categories[package.category].n_overlay += package.n_overlay

        for clog in categories.values():
            if not options['quiet']:
                self.stdout.write('[c] %s - [%d, %d/%d/%d]\n' %
                                  (clog.category, clog.n_packages,
                                   clog.n_packaged, clog.n_overlay, clog.n_versions))
            clog.save()

        for hlog in herds.values():
            if not options['quiet']:
                self.stdout.write('[h] %s - [%d, %d/%d/%d]\n' %
                                  (hlog.herd, hlog.n_packages,
                                   hlog.n_packaged, hlog.n_overlay, hlog.n_versions))
            hlog.save()

        for mlog in maintainers.values():
            if not options['quiet']:
                self.stdout.write('[m] %s - [%d, %d/%d/%d]\n' %
                                  (mlog.maintainer, mlog.n_packages,
                                   mlog.n_packaged, mlog.n_overlay, mlog.n_versions))
            mlog.save()
