import subprocess
from StringIO import StringIO

from django.conf import settings

from djeuscan.processing import FakeLogger


def _launch_command(cmd):
    """
    Helper for launching shell commands inside tasks
    """
    fp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    output = StringIO(fp.communicate()[0])
    return output.getvalue()


def emerge_sync():
    """
    Launches an emerge --sync
    """
    cmd = ["emerge", "--sync", "--root", settings.PORTAGE_ROOT,
           "--config-root", settings.PORTAGE_CONFIGROOT]
    return _launch_command(cmd)


def layman_sync():
    """
    Syncs Layman repos
    """
    from layman import Layman
    l = Layman(config=settings.LAYMAN_CONFIG)
    return l.sync(l.get_installed(), output_results=False)


def emerge_regen():
    """
    Launches emerge --regen
    """
    cmd = [
        "emerge", "--regen", "--jobs", settings.EMERGE_REGEN_JOBS, "--root",
        settings.PORTAGE_ROOT, "--config-root", settings.PORTAGE_CONFIGROOT
    ]
    return _launch_command(cmd)


def eix_update():
    """
    Launches eix-update
    """
    cmd = ["eix-update"]
    return _launch_command(cmd)


def update_portage_trees(logger=None):
    logger = logger or FakeLogger()
    logger.info("Running emerge --sync")
    emerge_sync()
    logger.info("Running layman --sync")
    layman_sync()
    logger.info("Running emerge --regen")
    emerge_regen()
    logger.info("Running eix-update")
    eix_update()
    logger.info("Done!")
