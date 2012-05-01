"""
tests for models
"""

from django.utils import unittest
from django.db import IntegrityError

from djeuscan.tests.euscan_factory import VersionFactory, PackageFactory


class VersionModelTests(unittest.TestCase):
    def test_creation(self):
        package = PackageFactory.build()
        version = VersionFactory.build(package=package)
        self.assertEqual(version.package, package)

    def test_not_allowed_creation(self):
        package = PackageFactory.create()
        VersionFactory.create(package=package)

        with self.assertRaises(IntegrityError):
            VersionFactory.create(package=package)
