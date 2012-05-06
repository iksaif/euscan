from urllib import urlencode

from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse


class SystemTestCase(unittest.TestCase):
    """
    Base class for system tests
    """

    def setUp(self):
        self.client = Client()

    def get(self, url_name, *args, **kwargs):
        param = kwargs.pop("param", None)
        if param:
            url = "%s?%s" % (reverse(url_name, args=args, kwargs=kwargs),
                             urlencode(param))
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)
        return self.client.get(url)

    def post(self, url_name, *args, **kwargs):
        data = kwargs.pop("data", {})
        url = reverse(url_name, args=args, kwargs=kwargs)
        return self.client.post(url, data)


from test_models import *
from test_views import *
from test_charts import *
