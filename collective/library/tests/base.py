import unittest
from plone.testing import z2
from plone.app.testing import SITE_OWNER_NAME

from collective.library.testing import LIBRARY_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = LIBRARY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
