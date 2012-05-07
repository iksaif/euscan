import StringIO
from BeautifulSoup import BeautifulSoup

from djeuscan.tests import SystemTestCase
from djeuscan.tests.euscan_factory import PackageFactory, HerdFactory, \
    MaintainerFactory, VersionFactory, random_string


class PagesTest(SystemTestCase):
    """
    Test main pages
    """

    def test_index(self):
        """
        Test index
        """
        response = self.get("index")
        self.assertEqual(response.status_code, 200)

    def test_world(self):
        response = self.get("world")
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.get("about")
        self.assertEqual(response.status_code, 200)


class SectionTests(SystemTestCase):
    def _check_table(self, response, items, attr=None):
        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        self.assertEqual(len(rows), len(items))

        for item in items:
            if attr:
                item_str = getattr(item, attr)
            else:
                item_str = item
            self.assertTrue(item_str in response.content)


class CategoriesTests(SectionTests):
    def setUp(self):
        super(CategoriesTests, self).setUp()
        self.categories = [PackageFactory.create().category
                           for _ in range(10)]

    def test_categories(self):
        response = self.get("categories")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.categories)


class HerdsTests(SectionTests):
    def setUp(self):
        super(HerdsTests, self).setUp()
        self.herds = [HerdFactory.create() for _ in range(10)]
        self.packages = []
        for i in range(0, 10, 2):
            p = PackageFactory.create()
            p.herds.add(self.herds[i])
            p.herds.add(self.herds[i + 1])
            self.packages.append(p)

    def test_herds(self):
        response = self.get("herds")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.herds, attr="herd")


class MaintainersTests(SectionTests):
    def setUp(self):
        super(MaintainersTests, self).setUp()
        self.maintainers = [MaintainerFactory.create() for _ in range(10)]
        self.packages = []
        for i in range(0, 10, 2):
            p = PackageFactory.create()
            p.maintainers.add(self.maintainers[i])
            p.maintainers.add(self.maintainers[i + 1])
            self.packages.append(p)

    def test_maintainers(self):
        response = self.get("maintainers")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.maintainers, attr="name")


class OverlayTests(SectionTests):
    def setUp(self):
        super(OverlayTests, self).setUp()
        self.overlays = [random_string() for _ in range(3)]

        for _ in range(3):
            self.package = PackageFactory.create()
            for overlay in self.overlays:
                VersionFactory.create(package=self.package,
                                      overlay=overlay)

    def test_overlays(self):
        response = self.get("overlays")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.overlays)


class WorldScanTests(SectionTests):
    def setUp(self):
        super(WorldScanTests, self).setUp()
        for _ in range(3):
            PackageFactory.create()
        self.packages = [PackageFactory.create().name for _ in range(3)]

    def test_world_scan_packages(self):
        response = self.post("world_scan",
                             data={"packages": "\n".join(self.packages)})
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages)

    def test_world_scan_world(self):
        world_file = StringIO.StringIO()
        world_file.write("\n".join(self.packages))
        world_file.name = "world"
        world_file.read = world_file.getvalue

        response = self.post("world_scan", data={"world": world_file})

        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages)
