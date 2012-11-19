"""
djeuscan.helpers
"""

from distutils.version import StrictVersion, LooseVersion
from django.shortcuts import get_object_or_404
from django.conf import settings

from layman import Layman

from portage.util import getconfig


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
        if pkg.count('/') == 1:
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


def get_maintainer_or_404(id=None, email=None):
    from djeuscan.models import Maintainer
    if id:
        return get_object_or_404(Maintainer, pk=id)
    else:
        return get_object_or_404(Maintainer, email=email)


def get_make_conf():
    return getconfig(settings.MAKE_CONF, tolerant=1, allow_sourcing=True)


def get_layman_repos():
    lay = Layman(config=settings.LAYMAN_CONFIG)
    installed_overlays = lay.get_installed()
    return lay.get_all_info(installed_overlays)


def versiontag_to_attrs(tag):
    import re
    match = re.match(r"(.+)-(.+)-(.+)", tag)
    if match:
        return match.groups()
    else:
        None
