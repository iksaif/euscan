import subprocess
from StringIO import StringIO
from itertools import islice

from celery.task import task, periodic_task
from celery.task.schedules import crontab
from celery.task.sets import TaskSet

from django.conf import settings

from euscan import output as euscan_output

from djeuscan.models import Package, RefreshPackageQuery
from djeuscan.management.commands.regen_rrds import regen_rrds
from djeuscan.management.commands.update_counters import update_counters
from djeuscan.management.commands.scan_metadata import ScanMetadata
from djeuscan.management.commands.scan_portage import ScanPortage, \
    purge_versions as scan_portage_purge
from djeuscan.management.commands.scan_upstream import ScanUpstream, \
    purge_versions as scan_upstream_purge


class TaskFailedException(Exception):
    """
    Exception for failed tasks
    """
    pass


def _launch_command(cmd):
    """
    Helper for launching shell commands inside tasks
    """
    fp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    output = StringIO(fp.communicate()[0])
    return output.getvalue()


def _chunks(it, n):
    """
    Chunk generator, takes an iterator and the desired size of the chunk
    """
    for first in it:
        yield [first] + list(islice(it, n - 1))


def _run_in_chunks(task, iterable, n=32):
    """
    Runs the given task with the given iterable of args in chunks of
    n subtasks
    """
    output = []
    for chunk in _chunks(iter(iterable), n):
        job = TaskSet(tasks=[
            task.subtask(args)
            for args in chunk
        ])
        result = job.apply_async()
        # TODO: understand why this causes timeout
        #output.extend(list(result.join(timeout=3600)))
    return output


@task
def regen_rrds_task():
    return regen_rrds()


@task
def update_counters_task():
    return update_counters()


@task
def scan_metadata_task(query, obj=None):
    logger = scan_metadata_task.get_logger()
    logger.info("Starting metadata scanning for package %s ...", query)

    scan_metadata = ScanMetadata()
    result = scan_metadata.scan(query, obj)
    if not result:
        raise TaskFailedException("Couldn't scan metadata")
    return result


@task
def scan_metadata_list_task(query):
    return _run_in_chunks(scan_metadata_task, [(p, ) for p in query.split()])


@task
def scan_metadata_all_task():
    return _run_in_chunks(
        scan_metadata_task,
        [('%s/%s' % (pkg.category, pkg.name), pkg)
         for pkg in Package.objects.all()]
    )


@task
def scan_portage_list_task(query, purge=False):
    scan_portage = ScanPortage()
    logger = scan_portage_list_task.get_logger()

    for pkg in query.split():
        logger.info("Starting Portage package scanning: %s ...", pkg)

        scan_portage.scan(pkg)

    if purge:
        logger.info("Purging")
        scan_portage_purge()


@task
def scan_portage_all_task(purge=False):
    logger = scan_portage_all_task.get_logger()
    logger.info("Starting Portage scanning...")

    scan_portage = ScanPortage()
    scan_portage.scan()

    if purge:
        logger.info("Purging")
        scan_portage_purge()


@task
def scan_upstream_task(query):
    logger = scan_upstream_task.get_logger()
    logger.info("Starting upstream scanning for package %s ...", query)

    euscan_output.clean()
    scan_upstream = ScanUpstream()
    result = scan_upstream.scan(query)
    euscan_output.clean()
    if not result or result == {}:
        raise TaskFailedException("Couldn't scan upstream")
    return result


@task
def scan_upstream_list_task(query):
    return _run_in_chunks(scan_upstream_task, [(p, ) for p in query.split()])


@task
def scan_upstream_all_task(purge=False):
    output = _run_in_chunks(
        scan_upstream_task,
        [('%s/%s' % (pkg.category, pkg.name), )
         for pkg in Package.objects.all()],
        n=16
    )

    if purge:
        output += [scan_upstream_purge()]

    return output


@task
def emerge_sync():
    cmd = ["emerge", "--sync", "--root", settings.PORTAGE_ROOT,
           "--config-root", settings.PORTAGE_CONFIGROOT]
    return _launch_command(cmd)


@task
def layman_sync():
    from layman import Layman
    l = Layman(config=settings.LAYMAN_CONFIG)
    return l.sync(l.get_installed(), output_results=False)


@task
def emerge_regen():
    cmd = [
        "emerge", "--regen", "--jobs", settings.EMERGE_REGEN_JOBS, "--root",
        settings.PORTAGE_ROOT, "--config-root", settings.PORTAGE_CONFIGROOT
    ]
    return _launch_command(cmd)


@task
def eix_update():
    cmd = ["eix-update"]
    return _launch_command(cmd)


@periodic_task(run_every=crontab(minute="*/1"))
def refresh_package_consume():
    try:
        obj = RefreshPackageQuery.objects.latest()
    except RefreshPackageQuery.DoesNotExist:
        return {}
    else:
        result = scan_upstream_task(obj.query)
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
    emerge_sync,
    layman_sync,
    emerge_regen,
    eix_update,
]
