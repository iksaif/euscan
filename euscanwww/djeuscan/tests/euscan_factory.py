import random
from string import letters
from datetime import datetime
from collections import defaultdict

from django.contrib.auth.models import User

import factory

from djeuscan.models import Herd, Maintainer, Package, Version, EuscanResult


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user' + n)


def random_string(length=None):
    if length is None:
        length = random.randint(1, 30)
    return "".join([random.choice(letters) for _ in range(length)])


class HerdFactory(factory.Factory):
    FACTORY_FOR = Herd

    herd = factory.LazyAttribute(lambda a: random_string())
    email = factory.LazyAttribute(lambda a: "%s@example.com" % a.herd)


class MaintainerFactory(factory.Factory):
    FACTORY_FOR = Maintainer

    name = factory.LazyAttribute(lambda a: random_string())
    email = factory.LazyAttribute(lambda a: "%s@example.com" % a.name)


class PackageFactory(factory.Factory):
    FACTORY_FOR = Package

    category = factory.LazyAttribute(
        lambda a: "%s-%s" % (random_string(), random_string())
    )
    name = factory.LazyAttribute(lambda a: random_string())
    description = "This is a test package"
    homepage = "http://testpackage.com"


class VersionFactory(factory.Factory):
    FACTORY_FOR = Version

    package = factory.LazyAttribute(lambda a: PackageFactory())
    slot = "1"
    revision = "1"
    version = "0.1"
    packaged = True
    overlay = "gentoo"
    urls = "http://packageurl.com"
    alive = True


class EuscanResultFactory(factory.Factory):
    FACTORY_FOR = EuscanResult

    package = factory.LazyAttribute(lambda a: PackageFactory())
    datetime = datetime.now()
    result = "this is the result"


def setup_maintainers():
    maintainers = [MaintainerFactory.create() for _ in range(10)]
    packages = []
    for i in range(0, 10, 2):
        p = PackageFactory.create()
        p.maintainers.add(maintainers[i])
        p.maintainers.add(maintainers[i + 1])
        packages.append(p)
    return maintainers, packages


def setup_categories():
    packages = [PackageFactory.create() for _ in range(10)]
    categories = [p.category for p in packages]
    return categories, packages


def setup_herds():
    herds = [HerdFactory.create() for _ in range(10)]
    packages = []

    for i in range(0, 10, 2):
        p = PackageFactory.create()
        p.herds.add(herds[i])
        p.herds.add(herds[i + 1])
        packages.append(p)
    return herds, packages


def setup_overlays():
    overlays = [random_string() for _ in range(3)]
    packages = defaultdict(list)

    for _ in range(3):
        package = PackageFactory.create()
        for overlay in overlays:
            VersionFactory.create(package=package,
                                  overlay=overlay)
            packages[overlay].append(package)

    return overlays, packages
