# -*- coding: utf-8 -*-

from plone.api import portal as portal_api


def upgrade_to_1002(portal_setup):
    portal_setup.runAllImportStepsFromProfile('profile-collective.library:upgrade1002')


def upgrade_to_1003(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'catalog')
    catalog = portal_api.get_tool('portal_catalog')
    catalog.refreshCatalog()


def upgrade_to_1004(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'catalog')
    catalog = portal_api.get_tool('portal_catalog')
    catalog.refreshCatalog()


def upgrade_to_1005(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'plone.app.registry')


def upgrade_to_1006(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'plone.app.registry')


def upgrade_to_1007(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'plone.app.registry')

def upgrade_to_1008(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'plone.app.registry')

def upgrade_to_1009(portal_setup):
    portal_setup.runImportStepFromProfile('profile-collective.library:default',
                                          'plone.app.registry')
