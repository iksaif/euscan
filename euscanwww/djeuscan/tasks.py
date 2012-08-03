"""
Celery tasks for djeuscan
"""

from celery.task import task, group

from django.conf import settings
from django.core.cache import cache

import portage

from djeuscan.models import Package, RefreshPackageQuery
from djeuscan.processing import scan, misc


class TaskFailedException(Exception):
    """
    Exception for failed tasks
    """
    pass


def group_one(task, seq, *args, **kwargs):
    """
    Create a group of tasks, each task handle one element of seq
    """
    tasks = []

    if "attr_name" in kwargs:
        attr_name = kwargs['attr_name']
        del kwargs["attr_name"]
    else:
        attr_name = None

    for elem in seq:
        if attr_name:
            kwargs[attr_name] = elem
            tasks.append(task.subtask(args=args, kwargs=dict(kwargs)))
        else:
            tasks.append(task.subtask(args=[elem] + list(args), kwargs=dict(kwargs)))
    return group(tasks)


def group_chunks(task, seq, n, *args, **kwargs):
    """
    Creates a group of tasks, each subtask has <n> elements to handle
    """
    tasks = []
    for i in xrange(0, len(seq), n):
        tasks.append(
            task.subtask(args=[seq[i:i + n]] + list(args), kwargs=kwargs)
        )
    return group(tasks)


@task
def regen_rrds():
    """
    Regenerate RRDs
    """
    misc.regen_rrds()
    return True


@task
def update_counters(fast=False):
    """
    Updates counters
    """
    logger = update_counters.get_logger()
    logger.info("Updating counters (fast=%s)...", fast)
    misc.update_counters(fast=fast)
    logger.info("Done")
    return True


@task
def scan_metadata(packages=[], category=None, populate=False):
    """
    Scans metadata for the given set of packages
    """
    logger = scan_metadata.get_logger()

    if packages:
        logger.info("Starting metadata scan for %d packages...",
                    len(packages))
    elif category:
        logger.info("Starting metadata scan for %s...",
                    category)
    else:
        logger.info("Starting metadata scan...")

    scan.scan_metadata(
        packages=packages,
        category=category,
        logger=logger,
        populate=populate,
    )
    return True


@task
def scan_portage(packages=[], category=None,
                 no_log=False, purge_packages=False,
                 purge_versions=False, prefetch=False):
    """
    Scans portage for the given set of packages
    """
    logger = scan_portage.get_logger()

    if packages:
        logger.info("Starting portage scan for %d packages...",
                    len(packages))
    elif category:
        logger.info("Starting portage scan for %s...",
                    category)
    else:
        logger.info("Starting portage scan...")

    scan.scan_portage(
        packages=packages,
        category=category,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
        prefetch=prefetch,
        logger=logger,
    )
    return True


@task
def scan_upstream(packages=[], purge_versions=False):
    """
    Scans upstream for the given set of packages
    """
    logger = scan_upstream.get_logger()

    if len(packages):
        logger.info("Starting upstream scan subtask for %d packages...",
                    len(packages))
    else:
        logger.info("Starting upstream scan...",
                    len(packages))

    scan.scan_upstream(
        packages=packages,
        purge_versions=purge_versions,
        logger=logger,
    )
    return True


@task
def update_portage_trees():
    """
    Update portage tree
    """
    logger = update_portage_trees.get_logger()
    misc.update_portage_trees(logger=logger)
    return True


@task
def update_portage(packages=None):
    update_portage_trees()
    scan_metadata(packages=None, populate=True)
    (
        group_one(scan_portage, portage.settings.categories,
                  attr_name="category", purge_packages=True,
                  purge_versions=True, prefetch=True) |
        group_one(scan_metadata, portage.settings.categories,
                  attr_name="category") |
        update_counters.si(fast=False)
    )()
    return True


@task
def update_upstream():
    if settings.TASKS_UPSTREAM_GROUPS >= 1:
        packages = Package.objects.all().order_by('pk')  # .order_by('?') ?

        scan_upstream_sub = group_chunks(scan_upstream, packages,
                                         settings.TASKS_UPSTREAM_GROUPS,
                                         purge_versions=True)
    else:
        scan_upstream_sub = scan_upstream.si(purge_versions=True)

    (
        scan_upstream_sub |
        update_counters.si(fast=False)
    )()
    return True


@task
def scan_package(package):
    scan_portage([package], purge_packages=True, purge_versions=True)
    scan_metadata([package])
    scan_upstream([package])
    return True


@task(rate_limit="1/m")
def scan_package_user(package):
    scan_package(package)
    return True


@task
def consume_refresh_queue(locked=False):
    """
    Satisfies user requests for package refreshing, runs every minute
    """
    LOCK_ID = 'lock-consume-refresh-queue'
    unlock = lambda: cache.delete(LOCK_ID)
    lock = lambda: cache.add(LOCK_ID, True, 120)

    logger = consume_refresh_queue.get_logger()

    if not locked and not lock():
        return

    logger.info('Consumming package refresh request queue...')

    try:
        query = RefreshPackageQuery.objects.all().order_by('-priority')[0]
        pkg = query.package
        query.delete()
        scan_package_user.delay(pkg)
        logger.info('Done (%s)' % pkg)
    except IndexError:
        pass
    finally:
        unlock()

    if RefreshPackageQuery.objects.count():
        logger.info('Restarting myself in 60s')
        lock()
        consume_refresh_queue.apply_async(kwargs={'locked':True}, countdown=60)

admin_tasks = [
    regen_rrds,
    update_counters,
    scan_metadata,
    scan_portage,
    scan_upstream,
    update_portage_trees,
    update_portage,
    update_upstream,
    scan_package,
]
