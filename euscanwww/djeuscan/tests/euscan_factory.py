import random
from string import letters
import factory
from datetime import datetime

from djeuscan.models import Herd, Maintainer, Package, Version, EuscanResult


def random_string(length=10):
    return "".join([random.choice(letters) for _ in range(length)])


class HerdFactory(factory.Factory):
    FACTORY_FOR = Herd

    herd = 'Test Herd'
    email = 'herd@testherd.com'


class MaintainerFactory(factory.Factory):
    FACTORY_FOR = Maintainer

    herd = 'Test Maintainer'
    email = 'maintainer@testmaintainer.com'


class PackageFactory(factory.Factory):
    FACTORY_FOR = Package

    category = factory.LazyAttribute(lambda a: random_string())
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
