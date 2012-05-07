from BeautifulSoup import BeautifulSoup

from djeuscan.tests import SystemTestCase
from djeuscan.tests.euscan_factory import PackageFactory, HerdFactory, \
    MaintainerFactory, VersionFactory, random_string


class NavigationTest(SystemTestCase):
    """
    Test main pages
    """

    def test_index(self):
        """
        Test index
        """
        response = self.get("index")
        self.assertEqual(response.status_code, 200)

    def test_categories(self):
        categories = [PackageFactory.create().category
                      for _ in range(10)]

        response = self.get("categories")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        self.assertEqual(len(rows), len(categories))

        for category in categories:
            self.assertTrue(category in response.content)

    def test_herds(self):
        herds = [HerdFactory.create() for _ in range(10)]
        packages = []
        for i in range(0, 10, 2):
            p = PackageFactory.create()
            p.herds.add(herds[i])
            p.herds.add(herds[i + 1])
            packages.append(p)

        response = self.get("herds")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        self.assertEqual(len(rows), len(herds))

        for herd in herds:
            self.assertTrue(herd.herd in response.content)

    def test_maintainers(self):
        maintainers = [MaintainerFactory.create() for _ in range(10)]
        packages = []
        for i in range(0, 10, 2):
            p = PackageFactory.create()
            p.maintainers.add(maintainers[i])
            p.maintainers.add(maintainers[i + 1])
            packages.append(p)

        response = self.get("maintainers")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        self.assertEqual(len(rows), len(maintainers))

        for maintainer in maintainers:
            self.assertTrue(maintainer.name in response.content)

    def test_overlays(self):
        overlays = [random_string() for _ in range(3)]

        for _ in range(3):
            package = PackageFactory.create()
            for overlay in overlays:
                VersionFactory.create(package=package, overlay=overlay)

        response = self.get("overlays")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        self.assertEqual(len(rows), len(overlays))

        for overlay in overlays:
            self.assertTrue(overlay in response.content)

    def test_world(self):
        response = self.get("world")
        self.assertEqual(response.status_code, 200)
