from urllib import urlencode

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from djeuscan.tests.euscan_factory import UserFactory


class SystemTestCase(TestCase):
    """
    Base class for system tests
    """
    fixtures = ["test_data.json"]

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

    def login(self):
        user = UserFactory.build()
        user.set_password("pass")
        user.save()
        return Login(self, user.username, "pass")


class Login(object):
    def __init__(self, testcase, user, password):
        self.testcase = testcase
        success = testcase.client.login(username=user, password=password)
        self.testcase.assertTrue(
            success,
            "login with username=%r, password=%r failed" % (user, password)
        )

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.testcase.client.logout()

from test_models import *
from test_views import *
from test_charts import *
