import factory
from djeuscan.models import Herd, Maintainer, Package, Version


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

    category = "Test Category"
    name = "Test Package"
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
