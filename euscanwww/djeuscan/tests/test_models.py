"""
tests for models
"""

from datetime import datetime

from django.test import TestCase
from django.db import IntegrityError
from django.utils.timezone import utc

from djeuscan.models import Package, EuscanResult
from djeuscan.tests.euscan_factory import VersionFactory, PackageFactory, \
    EuscanResultFactory, setup_maintainers, setup_herds, setup_categories, \
    setup_overlays


class VersionModelTests(TestCase):
    def test_creation(self):
        package = PackageFactory.build()
        version = VersionFactory.build(package=package)
        self.assertEqual(version.package, package)

    def test_not_allowed_creation(self):
        package = PackageFactory.create()
        VersionFactory.create(package=package)

        with self.assertRaises(IntegrityError):
            VersionFactory.create(package=package)


class PackageModelTests(TestCase):
    def test_homepages(self):
        homepage = "http://gentoo.org http://mypackage.com"
        package = PackageFactory.build(homepage=homepage)
        self.assertEqual(package.homepages,
                         ["http://gentoo.org", "http://mypackage.com"])

    def test_for_maintainer(self):
        maintainers, packages = setup_maintainers()
        maintainer = maintainers[0]
        self.assertEqual(
            list(Package.objects.for_maintainer(maintainer)),
            packages[:1]
        )

    def test_for_herd(self):
        herds, packages = setup_herds()
        herd = herds[0]
        self.assertEqual(
            list(Package.objects.for_herd(herd)),
            packages[:1]
        )

    def test_for_category(self):
        categories, packages = setup_categories()
        category = categories[0]
        self.assertEqual(
            list(Package.objects.for_category(category)),
            packages[:1]
        )

    def test_for_overlay(self):
        overlays, packages = setup_overlays()
        overlay = overlays[0]

        package_ids = [p.pk for p in packages[overlay]]
        for package in Package.objects.for_overlay(overlay):
            self.assertTrue(package["id"] in package_ids)

    def test_maintainers(self):
        maintainers, packages = setup_maintainers()
        maintainer_ids = [m.pk for m in maintainers]
        for maintainer in Package.objects.maintainers():
            self.assertTrue(maintainer["maintainers__id"] in maintainer_ids)

    def test_herds(self):
        herds, packages = setup_herds()
        herd_names = [h.herd for h in herds]
        for herd in Package.objects.herds():
            self.assertTrue(herd["herds__herd"] in herd_names)

    def test_categories(self):
        categories, packages = setup_categories()
        cat_names = [c["category"] for c in Package.objects.categories()]
        for category in categories:
            self.assertTrue(category in cat_names)

    def test_overlays(self):
        overlays, packages = setup_overlays()
        overlay_names = [o["version__overlay"]
                         for o in Package.objects.overlays()]
        for overlay in overlays:
            self.assertTrue(overlay in overlay_names)


class EuscanResultModelTests(TestCase):
    def test_lastest(self):
        result1 = EuscanResultFactory.create(
            datetime=datetime(2012, 04, 01, 12, 0, 0, 0, utc)
        )
        result2 = EuscanResultFactory.create(
            datetime=datetime(2012, 01, 01, 12, 0, 0, 0, utc)
        )
        self.assertEqual(result1, EuscanResult.objects.latest())
        self.assertNotEqual(result2, EuscanResult.objects.latest())
