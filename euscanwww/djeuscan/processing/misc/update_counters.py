from django.db.transaction import commit_on_success
from django.utils import timezone

from djeuscan.models import Package, Herd, Maintainer, Version
from djeuscan.models import HerdLog, MaintainerLog, CategoryLog, WorldLog
from djeuscan import charts
from djeuscan.processing import FakeLogger

from distutils.version import StrictVersion, LooseVersion


def _compare_versions(version1, version2):
    try:
        return cmp(StrictVersion(version1), StrictVersion(version2))
    # in case of abnormal version number, fall back to LooseVersion
    except ValueError:
        return cmp(LooseVersion(version1), LooseVersion(version2))


def _add_safe(storage, key):
    if key not in storage:
        storage[key] = 1
    else:
        storage[key] += 1


def _add_last_ver(storage, version):
    key = version['package_id']
    if key not in storage:
        storage[key] = version
        return
    if version['version'].startswith('9999'):
        return
    if _compare_versions(storage[key]['version'],
                        version['version']) < 0:
        storage[key] = version


@commit_on_success
def update_counters(fast=False, nolog=False, logger=None):
    logger = logger or FakeLogger()

    now = timezone.now()

    categories = {}
    herds = {}
    maintainers = {}

    wlog = None

    if not nolog:
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

    if not fast:
        attrs = ['id', 'version', 'overlay', 'packaged', 'package_id']
        for version in Version.objects.all().values(*attrs):
            overlay, packaged = version['overlay'], version['packaged']
            package_id = version['package_id']

            _add_safe(n_versions, package_id)

            if not packaged:
                _add_last_ver(last_versions_upstream, version)
                continue
            if overlay == 'gentoo':
                _add_safe(n_packaged, package_id)
                _add_last_ver(last_versions_gentoo, version)
            else:
                _add_safe(n_overlay, package_id)
                _add_last_ver(last_versions_overlay, version)

    for package in package_queryset.select_related('herds', 'maintainers'):
        if not fast:
            package.n_versions = n_versions.get(package.id, 0)
            package.n_packaged = n_packaged.get(package.id, 0)
            package.n_overlay = n_overlay.get(package.id, 0)

            default = {'id': None}
            package.last_version_gentoo_id = last_versions_gentoo.get(
                package.id, default
            )['id']
            package.last_version_overlay_id = last_versions_overlay.get(
                package.id, default
            )['id']
            package.last_version_upstream_id = last_versions_upstream.get(
                package.id, default
            )['id']

            package.save()

        n_packages_gentoo = int(package.n_packaged == package.n_versions)
        n_packages_overlay = int(package.n_overlay and package.n_packaged \
                                 + package.n_overlay == package.n_versions)
        n_packages_outdated = int(package.n_packaged + package.n_overlay \
                                  < package.n_versions)

        def update_row(storage, key):
            storage[key].n_packages_gentoo += n_packages_gentoo
            storage[key].n_packages_overlay += n_packages_overlay
            storage[key].n_packages_outdated += n_packages_outdated

            storage[key].n_versions_gentoo += package.n_packaged
            storage[key].n_versions_overlay += package.n_overlay
            storage[key].n_versions_upstream += package.n_versions - \
                                                package.n_packaged - \
                                                package.n_overlay

        def update_log(storage, qs):
            for row in qs:
                update_row(storage, row['id'])

        if not nolog:
            update_log(herds, package.herds.all().values('id'))
            update_log(maintainers, package.maintainers.all().values('id'))
            update_row(categories, package.category)

            wlog.n_packages_gentoo += n_packages_gentoo
            wlog.n_packages_overlay += n_packages_overlay
            wlog.n_packages_outdated += n_packages_outdated

            wlog.n_versions_gentoo += package.n_packaged
            wlog.n_versions_overlay += package.n_overlay
            wlog.n_versions_upstream += package.n_versions - \
                                        package.n_packaged - \
                                        package.n_overlay

    if nolog:
        return

    for clog in categories.values():
        logger.info('+ [cl] %s' % clog)
        charts.rrd_update('category-%s' % clog.category, now, clog)
        clog.save()

    for hlog in herds.values():
        logger.info('+ [hl] %s' % hlog)
        charts.rrd_update('herd-%d' % hlog.herd.id, now, hlog)
        hlog.save()

    for mlog in maintainers.values():
        logger.info('+ [ml] %s' % mlog)
        charts.rrd_update('maintainer-%d' % mlog.maintainer.id, now, mlog)
        mlog.save()

    charts.rrd_update('world', now, wlog)
    wlog.save()
