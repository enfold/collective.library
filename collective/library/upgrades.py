# -*- coding: utf-8 -*-


def upgrade_to_1002(portal_setup):
    portal_setup.runAllImportStepsFromProfile('profile-collective.library:upgrade1002')
