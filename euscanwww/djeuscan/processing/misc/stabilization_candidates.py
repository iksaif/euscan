import os.path
import re
from datetime import datetime, timedelta
from gentoolkit.package import Package
from dateutil.parser import  parse

from djeuscan.processing import FakeLogger
from djeuscan.models import Version


def get_version_date(version, date_limit):
    """
    Returns the datetime when the version was added to Portage, if less than date_limit
    """
    changelog_path = os.path.join(os.path.dirname(version.ebuild_path), "ChangeLog")
    if not os.path.exists(changelog_path):
        return

    with open(changelog_path) as changelog:
        for line in changelog:
            match = re.match(r"^\*([^\(]+) \((\d\d \w\w\w \d\d\d\d)\)\s*$", line)
            if match:
                version_date = parse(match.group(2)).date()
                if version_date < date_limit:
                    return version_date


def stabilization_candidates(date_limit=None, logger=None):
    """
    Collect stabilization candidates
    """

    if logger is None:
        logger = FakeLogger()

    if date_limit is None:
        date_limit = (datetime.utcnow() - timedelta(days=30)).date()

    logger.info("Starting collecting stabilization candidates - date_limit=%s", str(date_limit))

    # Set all versions to not be stabilization_candidates
    #Version.objects.update(stabilization_candidate=False)

    # For every version check if it's unstable.
    # If it is then check if can be a stabilization candidate
    for version in Version.objects.filter(overlay='gentoo').exclude(version='9999').exclude(version='99999999'):
        pkg = Package(version.cpv())
        keywords = pkg.environment("KEYWORDS").split()
        if all([x.startswith("~") for x in keywords]):
            version_date = get_version_date(version, date_limit)
            if version_date:
                logger.info('+ [s] %s @ %s', version, version_date)
                # XXX: What should we save? A flag and version_date? Just the date?
                #version.stabilization_candidate = True
                #version.save()

    logger.info("Finished collecting stabilization candidates")
