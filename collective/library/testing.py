# coding=utf-8
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import installProduct
from zope.configuration import xmlconfig

try:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
    BASE_FIXTURE = PLONE_APP_CONTENTTYPES_FIXTURE
except ImportError:
    from plone.app.testing import PLONE_FIXTURE
    BASE_FIXTURE = PLONE_FIXTURE


class LibraryLayer(PloneSandboxLayer):
    defaultBases = (BASE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import collective.library
        xmlconfig.file('configure.zcml', collective.library,
                       context=configurationContext)
        installProduct(app, 'collective.library')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'collective.library:default')
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))


LIBRARY_FIXTURE = LibraryLayer()
LIBRARY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(LIBRARY_FIXTURE,), name="Library:Integration")
LIBRARY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(LIBRARY_FIXTURE,), name="Library:Functional")
