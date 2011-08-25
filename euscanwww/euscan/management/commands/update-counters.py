import datetime

from optparse import make_option

from django.db.models import Count, Sum
from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand, CommandError
from euscanwww.euscan.models import Package, Herd, Maintainer, Version
from euscanwww.euscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from euscanwww.euscan import charts

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

        '''
        Could be done using raw SQL queries, but I don't have time for that
        right now ...
        '''

        wlog = WorldLog()
        wlog.datetime = now

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

            n_packages_gentoo = int(package.n_packaged == package.n_versions)
            n_packages_overlay = int(package.n_overlay and package.n_packaged + package.n_overlay == package.n_versions)
            n_packages_outdated = int(package.n_packaged + package.n_overlay < package.n_versions)

            for herd in package.herds.all():
                herds[herd].n_packages_gentoo   += n_packages_gentoo
                herds[herd].n_packages_overlay  += n_packages_overlay
                herds[herd].n_packages_outdated += n_packages_outdated

                herds[herd].n_versions_gentoo   += package.n_packaged
                herds[herd].n_versions_overlay  += package.n_overlay
                herds[herd].n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay

            for maintainer in package.maintainers.all():
                maintainers[maintainer].n_packages_gentoo   += n_packages_gentoo
                maintainers[maintainer].n_packages_overlay  += n_packages_overlay
                maintainers[maintainer].n_packages_outdated += n_packages_outdated

                maintainers[maintainer].n_versions_gentoo   += package.n_packaged
                maintainers[maintainer].n_versions_overlay  += package.n_overlay
                maintainers[maintainer].n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay

            categories[package.category].n_packages_gentoo   += n_packages_gentoo
            categories[package.category].n_packages_overlay  += n_packages_overlay
            categories[package.category].n_packages_outdated += n_packages_outdated

            categories[package.category].n_versions_gentoo   += package.n_packaged
            categories[package.category].n_versions_overlay  += package.n_overlay
            categories[package.category].n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay

            wlog.n_packages_gentoo   += n_packages_gentoo
            wlog.n_packages_overlay  += n_packages_overlay
            wlog.n_packages_outdated += n_packages_outdated

            wlog.n_versions_gentoo   += package.n_packaged
            wlog.n_versions_overlay  += package.n_overlay
            wlog.n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay

        for clog in categories.values():
            if not options['quiet']:
                self.stdout.write('+ [cl] %s\n' % clog)
            charts.rrd_update('category-%s' % clog.category, now, clog)
            clog.save()

        for hlog in herds.values():
            if not options['quiet']:
                self.stdout.write('+ [hl] %s\n' % hlog)
            charts.rrd_update('herd-%d' % hlog.herd.id, now, hlog)
            hlog.save()

        for mlog in maintainers.values():
            if not options['quiet']:
                self.stdout.write('+ [ml] %s\n' % mlog)
            charts.rrd_update('maintainer-%d' % mlog.maintainer.id, now, mlog)
            mlog.save()

        wlog.save()

        charts.rrd_update('world', now, wlog)
