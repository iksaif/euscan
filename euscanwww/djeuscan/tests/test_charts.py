from euscanwww.djeuscan.tests import SystemTestCase


class ChartTests(SystemTestCase):
    """
    Test charts
    """

    def test_statistics(self):
        response = self.get("statistics")
        self.assertEqual(response.status_code, 200)

    def test_pie_versions(self):
        response = self.get("chart", chart="pie-versions")
        self.assertEqual(response.status_code, 200)

    def test_pie_packages(self):
        response = self.get("chart", chart="pie-packages")
        self.assertEqual(response.status_code, 200)

    def test_packages(self):
        response = self.get("chart", chart="packages")
        self.assertEqual(response.status_code, 200)

    def test_packages_options(self):
        response = self.get("chart", chart="packages-small")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="packages-weekly")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="packages-monthly")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="packages-yearly")
        self.assertEqual(response.status_code, 200)

    def test_packages_option_incorrect(self):
        response = self.get("chart", chart="packages-trololol")
        self.assertEqual(response.status_code, 404)

    def test_versions(self):
        response = self.get("chart", chart="versions")
        self.assertEqual(response.status_code, 200)

    def test_versions_options(self):
        response = self.get("chart", chart="versions-small")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="versions-weekly")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="versions-monthly")
        self.assertEqual(response.status_code, 200)

        response = self.get("chart", chart="versions-yearly")
        self.assertEqual(response.status_code, 200)

    def test_versions_option_incorrect(self):
        response = self.get("chart", chart="versions-trololol")
        self.assertEqual(response.status_code, 404)
