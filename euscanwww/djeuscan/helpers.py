"""
djeuscan.helpers
"""

from distutils.version import StrictVersion, LooseVersion


def xint(i):
    """
    Tries to cast to int, fallbacks to 0
    """
    try:
        return int(i)
    except Exception:
        return 0


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
