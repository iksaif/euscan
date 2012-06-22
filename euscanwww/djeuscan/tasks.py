"""
Celery tasks for djeuscan
"""

from itertools import islice

from celery.task import task, periodic_task
from celery.task.schedules import crontab
from celery.task.sets import TaskSet

from djeuscan.models import Package, RefreshPackageQuery
from djeuscan.processing.regen_rrds import regen_rrds
from djeuscan.processing.update_counters import update_counters
from djeuscan.processing.scan_metadata import scan_metadata
from djeuscan.processing.scan_portage import scan_portage
from djeuscan.processing.scan_upstream import scan_upstream
from djeuscan.processing.update_portage_trees import update_portage_trees


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


def _run_in_chunks(task, packages, kwargs=None, concurrently=8, n=32):
    """
    Launches a TaskSet at a time with <concurrently> subtasks.
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
        job = TaskSet(tasks=tasks)
        result = job.apply_async()
        # TODO: understand why this causes timeout
        output.extend(list(result.join(timeout=3600)))
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

    result = scan_metadata(
        packages=packages,
        logger=logger,
    )
    if not result:
        raise TaskFailedException
    return result


@task
def scan_metadata_list_task(query):
    """
    Runs a parallel metadata scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """
    _run_in_chunks(_scan_metadata_task, [p for p in query.split()])


@task
def scan_metadata_all_task():
    """
    Runs a parallel metadata scan for all packages
    """
    _run_in_chunks(_scan_metadata_task, Package.objects.all())


@task
def _scan_portage_task(packages, no_logs=False, purge_packages=False,
                       purge_versions=False, prefetch=False):
    """
    Scans portage for the given set of packages
    """
    logger = _scan_portage_task.get_logger()
    logger.info("Starting portage scanning subtask for %d packages...",
                len(packages))

    result = scan_portage(
        packages=packages,
        no_logs=no_logs,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
        prefetch=prefetch,
        logger=logger,
    )
    if not result:
        raise TaskFailedException
    return result


@task
def scan_portage_list_task(query, no_logs=False, purge_packages=False,
                           purge_versions=False, prefetch=False):
    """
    Runs a parallel portage scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """
    kwargs = {"no_logs": no_logs, "purge_packages": purge_packages,
              "purge_versions": purge_versions, "prefetch": prefetch}
    _run_in_chunks(_scan_portage_task, [p for p in query.split()], kwargs)


@task
def scan_portage_all_task(no_logs=False, purge_packages=False,
                          purge_versions=False, prefetch=False):
    """
    Runs a parallel portage scan for all packages
    """
    kwargs = {"no_logs": no_logs, "purge_packages": purge_packages,
              "purge_versions": purge_versions, "prefetch": prefetch}
    _run_in_chunks(_scan_metadata_task, Package.objects.all(), kwargs)


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
    if not result:
        raise TaskFailedException
    return result


@task
def scan_upstream_list_task(query, purge_versions=False):
    """
    Runs a parallel upstream scan for packages in the query list (space
    separated string). Task used only from the web interface.
    """

    kwargs = {"purge_versions": purge_versions}
    _run_in_chunks(_scan_upstream_task, [p for p in query.split()], kwargs)


@task
def scan_upstream_all_task(purge_versions=False):
    """
    Runs a parallel portage scan for all packages
    """
    kwargs = {"purge_versions": purge_versions}
    _run_in_chunks(_scan_upstream_task, Package.objects.all(), kwargs)


@task
def update_portage_trees_task():
    """
    Update portage tree
    """
    logger = update_portage_trees_task.get_logger()
    update_portage_trees(logger=logger)


@task
def update_task(update_portage_trees=True, scan_portage=True,
                scan_metadata=True, scan_upstream=True, update_counter=True):
    """
    Update the whole euscan system
    """
    if update_portage_trees:
        update_portage_trees_task()
    if scan_portage:
        scan_portage_all_task(prefetch=True, purge_packages=True,
                              purge_versions=True)

    # metadata and upstream scan can run concurrently, launch them
    # asynchronously and wait for them to finish
    metadata_job = None
    if scan_metadata:
        metadata_job = scan_metadata_all_task().delay()

    upstream_job = None
    if scan_upstream:
        upstream_job = scan_upstream_all_task().delay()

    if metadata_job:
        metadata_job.wait()
    if upstream_job:
        upstream_job.wait()

    update_counters(fast=False)


@task
def scan_package_task(package):
    _scan_portage_task([package], purge_packages=True, purge_versions=True)
    _scan_metadata_task([package])
    _scan_upstream_task([package])


@periodic_task(run_every=crontab(minute="*/1"))
def consume_refresh_package_request():
    """
    Satisfies user requests for package refreshing, runs every minute
    """
    try:
        obj = RefreshPackageQuery.objects.latest()
    except RefreshPackageQuery.DoesNotExist:
        return {}
    else:
        result = scan_package_task(obj.query)
        obj.delete()
        return result


@periodic_task(run_every=crontab(hour=03, minute=00, day_of_week=1))
def update_periodic_task():
    """
    Runs a whole update once a week
    """
    update_task()


admin_tasks = [
    regen_rrds_task,
    update_counters_task,
    scan_metadata_list_task,
    scan_metadata_all_task,
    scan_portage_all_task,
    scan_portage_list_task,
    scan_upstream_all_task,
    scan_upstream_list_task,
    update_portage_trees,
    update_task,
    scan_package_task,
]
