"""
Celery tasks for djeuscan
"""

from itertools import islice

from celery.task import task, group, chord

from django.conf import settings

from djeuscan.models import Package, RefreshPackageQuery
from djeuscan.processing.misc import regen_rrds, update_counters, \
    update_portage_trees
from djeuscan.processing.scan import scan_metadata, scan_portage, scan_upstream


class TaskFailedException(Exception):
    """
    Exception for failed tasks
    """
    pass


def _chunks(it, n):
    """
    Chunk generator, takes an iterator and the desired size of the chunk
    """
    for first in it:
        yield [first] + list(islice(it, n - 1))


def _run_in_chunks(task, packages, kwargs=None,
                   concurrently=settings.TASKS_CONCURRENTLY,
                   n=settings.TASKS_SUBTASK_PACKAGES):
    """
    Launches a group at a time with <concurrently> subtasks.
    Each subtask has <n> packages to handle
    """
    output = []

    chunk_generator = _chunks(iter(packages), n)
    done = False

    while not done:
        tasks = []
        for _ in range(concurrently):
            try:
                chunk = chunk_generator.next()
            except StopIteration:
                done = True
            else:
                tasks.append(task.subtask((chunk, ), kwargs))
        output.extend(group(tasks)())
    return output


@task
def regen_rrds_task():
    """
    Regenerate RRDs
    """
    return regen_rrds()


@task
def update_counters_task(fast=True):
    """
    Updates counters
    """
    return update_counters(fast=fast)


@task
def _scan_metadata_task(packages):
    """
    Scans metadata for the given set of packages
    """
    logger = _scan_metadata_task.get_logger()
    logger.info("Starting metadata scanning subtask for %d packages...",
                len(packages))

    scan_metadata(
        packages=packages,
        logger=logger,
    )


@task
def scan_metadata_list_task(query):
    """
    Runs a parallel metadata scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """
    return _run_in_chunks(_scan_metadata_task, [p for p in query.split()])


@task
def scan_metadata_all_task():
    """
    Runs a parallel metadata scan for all packages
    """
    return _run_in_chunks(_scan_metadata_task, Package.objects.all())


@task
def _scan_portage_task(packages, category=None, no_log=False,
                       purge_packages=False, purge_versions=False,
                       prefetch=False):
    """
    Scans portage for the given set of packages
    """
    logger = _scan_portage_task.get_logger()
    if packages:
        logger.info("Starting portage scanning subtask for %d packages...",
                    len(packages))
    else:
        logger.info("Starting portage scanning for all packages...")

    scan_portage(
        packages=packages,
        category=category,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
        prefetch=prefetch,
        logger=logger,
    )


@task
def scan_portage_list_task(query, no_log=False, purge_packages=False,
                           purge_versions=False, prefetch=False):
    """
    Runs a parallel portage scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """
    kwargs = {"no_log": no_log, "purge_packages": purge_packages,
              "purge_versions": purge_versions, "prefetch": prefetch}
    return _run_in_chunks(
        _scan_portage_task, [p for p in query.split()], kwargs
    )


@task
def scan_portage_all_task(no_log=False, purge_packages=False,
                          purge_versions=False, prefetch=False):
    """
    Runs a syncronous portage scan for all packages
    """
    _scan_portage_task(
        packages=None,
        category=None,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
        prefetch=prefetch,
    )


@task
def _scan_upstream_task(packages, purge_versions=False):
    """
    Scans upstream for the given set of packages
    """
    logger = _scan_upstream_task.get_logger()

    logger.info("Starting upstream scanning subtask for %d packages...",
                len(packages))

    result = scan_upstream(
        packages=packages,
        purge_versions=purge_versions,
        logger=logger,
    )
    # TODO: implement some kind of error raising in case of failure
    #if not result:
    #    raise TaskFailedException
    return result


@task
def scan_upstream_list_task(query, purge_versions=False):
    """
    Runs a parallel upstream scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """

    kwargs = {"purge_versions": purge_versions}
    return _run_in_chunks(_scan_upstream_task, [p for p in query.split()],
                          kwargs)


@task
def scan_upstream_all_task(purge_versions=False):
    """
    Runs a parallel portage scan for all packages
    """
    kwargs = {"purge_versions": purge_versions}
    return _run_in_chunks(
        _scan_upstream_task,
        Package.objects.all().order_by('?'),
        kwargs
    )


@task
def update_portage_trees_task():
    """
    Update portage tree
    """
    logger = update_portage_trees_task.get_logger()
    update_portage_trees(logger=logger)


@task
def update_task(update_portage_trees=True, scan_portage=True,
                scan_metadata=True, scan_upstream=True, update_counters=True):
    """
    Update the whole euscan system
    """
    if update_portage_trees:
        update_portage_trees_task()
    if scan_portage:
        scan_portage_all_task(prefetch=True, purge_packages=True,
                              purge_versions=True)

    # metadata and upstream scan can run concurrently, launch them
    # in a group and wait for them to finish
    tasks = []
    if scan_metadata:
        tasks.append(scan_metadata_all_task.subtask())

    if scan_upstream:
        tasks.append(scan_upstream_all_task.subtask())

    if update_counters:
        chord(tasks)(
            # immutable means that the result of previous tasks is not passed
            update_counters_task.subtask((), {"fast": False}, immutable=True)
        )
    else:
        group(tasks)()


@task
def scan_package_task(package):
    _scan_portage_task([package], purge_packages=True, purge_versions=True)
    _scan_metadata_task([package])
    _scan_upstream_task([package])


# Periodic tasks

@task
def consume_refresh_package_request():
    """
    Satisfies user requests for package refreshing, runs every minute
    """
    try:
        obj = RefreshPackageQuery.objects.all().order_by('-priority')[0]
    except IndexError:
        return {}
    else:
        result = scan_package_task(obj.package)
        obj.delete()
        return result


admin_tasks = [
    regen_rrds_task,
    update_counters_task,
    scan_metadata_list_task,
    scan_metadata_all_task,
    scan_portage_all_task,
    scan_portage_list_task,
    scan_upstream_all_task,
    scan_upstream_list_task,
    update_portage_trees_task,
    update_task,
    scan_package_task,
]
