from euscanwww.djeuscan.tests import SystemTestCase


class ChartTests(SystemTestCase):
    """
    Test main pages
    """

    def test_statistics(self):
        response = self.get("statistics")
        self.assertEqual(response.status_code, 200)

    def test_pie_versions(self):
        response = self.get("chart", chart="pie-versions")
        self.assertEqual(response.status_code, 200)
