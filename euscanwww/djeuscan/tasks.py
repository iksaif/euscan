import subprocess
from StringIO import StringIO

from celery.task import task
from celery.task.sets import TaskSet

from django.conf import settings

from djeuscan.models import Package
from djeuscan.management.commands.regen_rrds import regen_rrds
from djeuscan.management.commands.update_counters import update_counters
from djeuscan.management.commands.scan_metadata import ScanMetadata
from djeuscan.management.commands.scan_portage import ScanPortage, \
    purge_versions as scan_portage_purge
from djeuscan.management.commands.scan_upstream import ScanUpstream, \
    purge_versions as scan_upstream_purge


@task
def regen_rrds_task():
    regen_rrds()


@task
def update_counters_task():
    update_counters()


@task
def scan_metadata_task(query, obj=None):
    logger = scan_metadata_task.get_logger()
    logger.info("Starting metadata scanning for package %s ...", query)

    scan_metadata = ScanMetadata()
    scan_metadata.scan(query, obj)


@task
def scan_metadata_list_task(query):
    job = TaskSet(tasks=[
        scan_metadata_task.subtask((pkg, ))
        for pkg in query.split()
    ])
    job.apply_async()


@task
def scan_metadata_all_task():
    job = TaskSet(tasks=[
        scan_metadata_task.subtask(('%s/%s' % (pkg.category, pkg.name), pkg))
        for pkg in Package.objects.all()
    ])
    job.apply_async()


@task
def scan_portage_list_task(query, purge=False):
    scan_portage = ScanPortage()

    for pkg in query.split():
        logger = scan_portage_list_task.get_logger()
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
def scan_portage_purge_task():
    scan_portage_purge()


@task
def scan_upstream_task(query):
    logger = scan_upstream_task.get_logger()
    logger.info("Starting upstream scanning for package %s ...", query)

    scan_upstream = ScanUpstream()
    scan_upstream.scan(query)


@task
def scan_upstream_list_task(query):
    job = TaskSet(tasks=[
        scan_upstream_task.subtask((pkg, ))
        for pkg in query.split()
    ])
    job.apply_async()


@task
def scan_upstream_all_task(purge=False):
    tasks = [scan_upstream_task.subtask(('%s/%s' % (pkg.category, pkg.name), ))
             for pkg in Package.objects.all()]

    if purge:
        tasks.append(scan_upstream_purge_task.subtask())

    job = TaskSet(tasks=tasks)
    job.apply_async()


@task
def scan_upstream_purge_task():
    scan_upstream_purge()


def _launch_command(cmd):
    fp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    output = StringIO(fp.communicate()[0])
    return output.getvalue()


@task
def emerge_sync():
    cmd = ["emerge", "--sync", "--root", settings.PORTAGE_ROOT,
           "--config-root", settings.PORTAGE_CONFIGROOT]
    return _launch_command(cmd)


@task
def layman_sync():
    from layman import Layman
    results = []
    l = Layman()
    for overlay in l.get_installed():
        results.append(l.sync(overlay, output_results=False))
    return results


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


launchable_tasks = [
    regen_rrds_task,
    update_counters_task,
    scan_metadata_list_task,
    scan_metadata_all_task,
    scan_portage_all_task,
    scan_portage_list_task,
    scan_portage_purge_task,
    scan_upstream_all_task,
    scan_upstream_list_task,
    scan_upstream_purge_task,
    emerge_sync,
    layman_sync,
    emerge_regen,
    eix_update,
]
