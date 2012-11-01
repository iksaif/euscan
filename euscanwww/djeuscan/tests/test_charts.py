from djeuscan.tests import SystemTestCase
from djeuscan.tests.euscan_factory import MaintainerFactory, HerdFactory, \
    PackageFactory


class ChartTests(SystemTestCase):
    """
    Test charts
    """

    url = "chart"
    args = []
    kwargs = {}

    def test_statistics(self):
        response = self.get("statistics")
        self.assertEqual(response.status_code, 200)

    def test_pie_versions(self):
        response = self.get(self.url, chart="pie-versions",
                            *self.args, **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_pie_packages(self):
        response = self.get(self.url, chart="pie-packages", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_packages(self):
        response = self.get(self.url, chart="packages", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_packages_options(self):
        response = self.get(self.url, chart="packages-small", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="packages-weekly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="packages-monthly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="packages-yearly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_packages_option_incorrect(self):
        response = self.get(self.url, chart="packages-trololol", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_versions(self):
        response = self.get(self.url, chart="versions", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_versions_options(self):
        response = self.get(self.url, chart="versions-small", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="versions-weekly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="versions-monthly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

        response = self.get(self.url, chart="versions-yearly", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_versions_option_incorrect(self):
        response = self.get(self.url, chart="versions-trololol", *self.args,
                            **self.kwargs)
        self.assertEqual(response.status_code, 404)


class CategoryChartTests(ChartTests):
    def setUp(self):
        super(CategoryChartTests, self).setUp()
        self.url = "chart_category"
        self.kwargs = {"category": PackageFactory.create().category}


class HerdChartTests(ChartTests):
    def setUp(self):
        super(HerdChartTests, self).setUp()
        self.url = "chart_herd"
        self.kwargs = {"herd": HerdFactory.create().herd}


class MaintainerChartTests(ChartTests):
    def setUp(self):
        super(MaintainerChartTests, self).setUp()
        self.url = "chart_maintainer"
        self.kwargs = {"maintainer_id": MaintainerFactory.create().pk}
