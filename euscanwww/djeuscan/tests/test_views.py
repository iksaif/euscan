from euscanwww.djeuscan.tests import SystemTestCase


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
