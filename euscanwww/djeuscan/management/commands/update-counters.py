import datetime

from optparse import make_option

from django.db.models import Count, Sum
from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand, CommandError

from djeuscan.models import Package, Herd, Maintainer, Version
from djeuscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from djeuscan import charts

from distutils.version import StrictVersion, LooseVersion

def compare_versions(version1, version2):
    try:
        return cmp(StrictVersion(version1), StrictVersion(version2))
    # in case of abnormal version number, fall back to LooseVersion
    except ValueError:
        return cmp(LooseVersion(version1), LooseVersion(version2))

class Command(BaseCommand):
    _overlays = {}
    help = 'Update counters'

    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Be quiet'),
        make_option('--fast',
            action='store_true',
            dest='fast',
            default=False,
            help='Skip sanity checks'),
        make_option('--nolog',
            action='store_true',
            dest='nolog',
            default=False,
            help='Skip logs'),

        )

    @commit_on_success
    def handle(self, *args, **options):
        now = datetime.datetime.now()

        categories = {}
        herds = {}
        maintainers = {}

        wlog = None

        if not options['nolog']:
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
                herds[herd.id] = hlog

            for maintainer in Maintainer.objects.all():
                mlog = MaintainerLog()
                mlog.datetime = now
                mlog.maintainer = maintainer
                maintainers[maintainer.id] = mlog

        package_queryset = Package.objects.all()

        n_versions = {}
        n_packaged = {}
        n_overlay = {}

        last_versions_gentoo = {}
        last_versions_overlay = {}
        last_versions_upstream = {}

        def add_safe(storage, key):
            if key not in storage:
                storage[key] = 1
            else:
                storage[key] += 1

        def add_last_ver(storage, version):
            key = version['package_id']
            if key not in storage:
                storage[key] = version
                return
            if version['version'].startswith('9999'):
                return
            if compare_versions(storage[key]['version'], version['version']) < 0:
                storage[key] = version

        if not options['fast']:
            attrs = ['id', 'version', 'overlay', 'packaged', 'package_id']
            for version in Version.objects.all().values(*attrs):
                overlay, packaged = version['overlay'], version['packaged']
                package_id = version['package_id']

                add_safe(n_versions, package_id)

                if not packaged:
                    add_last_ver(last_versions_upstream, version)
                    continue
                if overlay == 'gentoo':
                    add_safe(n_packaged, package_id)
                    add_last_ver(last_versions_gentoo, version)
                else:
                    add_safe(n_overlay, package_id)
                    add_last_ver(last_versions_overlay, version)

        for package in package_queryset.select_related('herds', 'maintainers'):
            if not options['fast']:
                package.n_versions = n_versions.get(package.id, 0)
                package.n_packaged = n_packaged.get(package.id, 0)
                package.n_overlay = n_overlay.get(package.id, 0)

                default = {'id' : None}
                package.last_version_gentoo_id = last_versions_gentoo.get(package.id, default)['id']
                package.last_version_overlay_id = last_versions_overlay.get(package.id, default)['id']
                package.last_version_upstream_id = last_versions_upstream.get(package.id, default)['id']

                package.save()

            n_packages_gentoo = int(package.n_packaged == package.n_versions)
            n_packages_overlay = int(package.n_overlay and package.n_packaged + package.n_overlay == package.n_versions)
            n_packages_outdated = int(package.n_packaged + package.n_overlay < package.n_versions)

            def update_row(storage, key):
                storage[key].n_packages_gentoo   += n_packages_gentoo
                storage[key].n_packages_overlay  += n_packages_overlay
                storage[key].n_packages_outdated += n_packages_outdated

                storage[key].n_versions_gentoo   += package.n_packaged
                storage[key].n_versions_overlay  += package.n_overlay
                storage[key].n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay
            def update_log(storage, qs):
                for row in qs:
                    update_row(storage, row['id'])

            if not options['nolog']:
                update_log(herds, package.herds.all().values('id'))
                update_log(maintainers, package.maintainers.all().values('id'))
                update_row(categories, package.category)

                wlog.n_packages_gentoo   += n_packages_gentoo
                wlog.n_packages_overlay  += n_packages_overlay
                wlog.n_packages_outdated += n_packages_outdated

                wlog.n_versions_gentoo   += package.n_packaged
                wlog.n_versions_overlay  += package.n_overlay
                wlog.n_versions_upstream += package.n_versions - package.n_packaged - package.n_overlay

        if options['nolog']:
            return

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

        charts.rrd_update('world', now, wlog)
        wlog.save()
