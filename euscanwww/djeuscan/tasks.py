"""
Celery tasks for djeuscan
"""

from datetime import datetime

from celery.task import task, group

#import portage

from django.conf import settings
from django.core.cache import cache
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models import Q

from euscan.version import gentoo_unstable

from djeuscan.models import Package, RefreshPackageQuery, UserProfile, \
    VersionLog
from djeuscan.processing import scan, misc
from djeuscan.helpers import get_account_versionlogs, get_user_fav_infos


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
            tasks.append(task.subtask(args=list(args), kwargs=dict(kwargs),
                         immutable=True))
        else:
            tasks.append(task.subtask(args=[elem] + list(args),
                         kwargs=dict(kwargs), immutable=True))

    return group(tasks)


def group_chunks(task, seq, n, *args, **kwargs):
    """
    Creates a group of tasks, each subtask has <n> elements to handle
    """
    tasks = []
    for i in xrange(0, len(seq), n):
        tasks.append(
            task.subtask(args=[seq[i:i + n]] + list(args), kwargs=kwargs,
                         immutable=True)
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
def scan_portage(packages=None, category=None,
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

    return scan.scan_portage(
        packages=packages,
        category=category,
        no_log=no_log,
        purge_packages=purge_packages,
        purge_versions=purge_versions,
        prefetch=prefetch,
        logger=logger,
    )


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
        logger.info("Starting upstream scan...")

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
    #categories = portage.settings.categories

    # Workaround for celery bug when chaining groups
    update_portage_trees()
    updated_packages = scan_portage(
        packages=None,
        purge_packages=True,
        purge_versions=True,
        prefetch=True
    )
    scan_metadata(packages=None, populate=True)
    if updated_packages:
            group_chunks(scan_upstream, updated_packages,
                         settings.TASKS_UPSTREAM_GROUPS,
                         purge_versions=True)()
    update_counters(fast=False)

    """ Currently broken
    update_portage_trees()
    scan_metadata(packages=None, populate=True)
    (
        group_one(scan_portage, categories,
                  attr_name="category", purge_packages=True,
                  purge_versions=True, prefetch=True) |
        group_one(scan_metadata, categories,
                  attr_name="category") |
        update_counters.si(fast=True)
    )()
    """
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
        update_counters.si(fast=False) |
        send_update_email.si()
    )()
    return True


@task
def scan_package(package):
    logger = scan_package.get_logger()
    logger.info("Scanning package %s", package)
    scan_portage([package], purge_packages=True, purge_versions=True)
    scan_metadata([package])
    scan_upstream([package], purge_versions=True)
    return True


@task(rate_limit="1/m")
def scan_package_user(package):
    scan_package(package)
    return True


@task(rate_limit="1/m")
def consume_refresh_queue(locked=False):
    """
    Satisfies user requests for package refreshing, runs every minute
    """
    logger = consume_refresh_queue.get_logger()
    logger.info('Consuming package refresh request queue...')

    try:
        query = RefreshPackageQuery.objects.all().order_by('-priority')[0]
        pkg = query.package
        query.delete()
        scan_package_user.delay(pkg)
        logger.info('Selected: %s' % pkg)
    except IndexError:
        return

    if RefreshPackageQuery.objects.count():
        logger.info('Restarting myself in 60s')
        consume_refresh_queue.apply_async(
            kwargs={'locked': True}, countdown=60
        )
    return True

@task(max_retries=10, default_retry_delay=10 * 60)
def send_user_email(address, subject, text):
    try:
        send_mail(
            subject, text, settings.DEFAULT_FROM_EMAIL, [address],
            fail_silently=False
        )
    except Exception, exc:
        raise send_user_email.retry(exc=exc)
    return True

@task
def process_emails(profiles, only_if_vlogs=False):
    for profile in profiles:
        now = datetime.now()
        user = profile.user

        vlogs = get_account_versionlogs(profile)
        vlogs = vlogs.filter(
            datetime__gt=profile.last_email,
            overlay="",  # only upstream versions
            action=VersionLog.VERSION_ADDED,  # only adds
        )
        if profile.email_ignore_pre:
            vlogs = vlogs.exclude(vtype__in=gentoo_unstable)
        if profile.email_ignore_pre_if_stable:
            vlogs = vlogs.exclude(
                ~Q(package__last_version_gentoo__vtype__in=gentoo_unstable),
                vtype__in=gentoo_unstable
            )

        if only_if_vlogs and not vlogs.count():
            continue

        vlogs = vlogs.order_by("-datetime")

        infos = get_user_fav_infos(user)
        infos["user"] = user
        infos["vlogs"] = vlogs

        mail_text = render_to_string(
            "euscan/accounts/euscan_email.txt",
            infos
        )

        send_user_email.delay(
            user.email, "euscan updates - %s" % str(now.date()), mail_text
        )

        profile.last_email = now
        profile.save(force_update=True)
    return True

@task
def send_update_email():
    profiles = UserProfile.objects.filter(
        email_every=UserProfile.EMAIL_SCAN,
        email_activated=True
    )
    group_chunks(
        process_emails,
        profiles,
        settings.TASKS_EMAIL_GROUPS,
        only_if_vlogs=True
    )()
    return True


@task
def send_weekly_email():
    profiles = UserProfile.objects.filter(
        email_every=UserProfile.EMAIL_WEEKLY,
        email_activated=True
    )
    group_chunks(process_emails, profiles, settings.TASKS_EMAIL_GROUPS)()
    return True


@task
def send_monthly_email():
    profiles = UserProfile.objects.filter(
        email_every=UserProfile.EMAIL_MONTHLY,
        email_activated=True
    )
    group_chunks(process_emails, profiles, settings.TASKS_EMAIL_GROUPS)()
    return True

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
    send_update_email,
    send_weekly_email,
    send_monthly_email,
]
