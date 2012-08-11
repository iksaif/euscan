"""
djeuscan.helpers
"""

from distutils.version import StrictVersion, LooseVersion
from django.db.models import Q


def xint(i):
    """
    Tries to cast to int, fallbacks to 0
    """
    try:
        return int(i)
    except Exception:
        return 0


def select_related_last_versions(queryset):
    queryset = queryset.select_related(
        'last_version_gentoo',
        'last_version_overlay',
        'last_version_upstream'
    )


def version_key(version):
    version = version.version
    try:
        return StrictVersion(version)
    # in case of abnormal version number, fall back to LooseVersion
    except ValueError:
        return LooseVersion(version)


def packages_from_names(data):
    """
    Returns a list of Package objects from a string of names
    """

    from djeuscan.models import Package

    packages = []
    data = data.replace("\r", "")

    for pkg in data.split('\n'):
        if '/' in pkg:
            cat, pkg = pkg.split('/')
            packages.extend(Package.objects.filter(category=cat, name=pkg))
        else:
            packages.extend(Package.objects.filter(name=pkg))
    return packages


def rename_fields(vqs, fields):
    ret = []
    for n in vqs:
        for tr in fields:
            if tr[0] in n:
                n[tr[1]] = n[tr[0]]
                del n[tr[0]]
        ret.append(n)
    return ret


class catch_and_return(object):
    def __init__(self, err, response):
        self.err = err
        self.response = response

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except self.err:
                return self.response
        return wrapper


def get_profile(user):
    from djeuscan.models import UserProfile
    try:
        return user.get_profile()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)
        return user.get_profile()


def get_account_categories(user):
    from djeuscan.models import Package
    # TODO: This is quite ugly
    category_names = [obj.name for obj in get_profile(user).categories.all()]
    return [c for c in Package.objects.categories()
            if c["category"] in category_names]


def get_account_herds(user):
    from djeuscan.models import Package

    ids = [herd.pk for herd in get_profile(user).herds.all()]
    return Package.objects.herds(ids=ids)


def get_account_maintainers(user):
    from djeuscan.models import Package

    ids = [obj.pk for obj in get_profile(user).maintainers.all()]
    return Package.objects.maintainers(ids=ids)


def get_account_versionlogs(profile):
    """
    Returns all watched packages
    """
    from djeuscan.models import Package, VersionLog

    q_categories = Q(category__in=[
        category.name for category in profile.categories.all()])
    q_herds = Q(herds__in=profile.herds.all())
    q_maintainers = Q(maintainers__in=profile.maintainers.all())
    packages = list(profile.packages.all()) + list(Package.objects.filter(
        q_categories | q_herds | q_maintainers))

    overlays = [o.name for o in profile.overlays.all()]

    return VersionLog.objects.filter(
        Q(package__in=packages) | Q(overlay__in=overlays)
    )
