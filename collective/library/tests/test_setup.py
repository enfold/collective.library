from .base import BaseTestCase


class TestInstall(BaseTestCase):

    def setUp(self):
        from Products.CMFCore.utils import getToolByName
        super(TestInstall, self).setUp()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProducts(['collective.library'])

    def test_product_installed(self):
        from Products.CMFCore.utils import getToolByName
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(installer.isProductInstalled('collective.library'))

    def test_catalog_indexes_added(self):
        from Products.CMFCore.utils import getToolByName
        catalog = getToolByName(self.portal, 'portal_catalog')
        library_index = catalog._catalog.getIndex('library')
        self.assertEqual(library_index.meta_type, 'FieldIndex')
        library_path_index = catalog._catalog.getIndex('path_in_library')
        self.assertEqual(library_path_index.meta_type, 'ExtendedPathIndex')
        parent_libraries_index = catalog._catalog.getIndex('parent_libraries')
        self.assertEqual(parent_libraries_index.meta_type, 'KeywordIndex')

    def test_types_added(self):
        from Products.CMFCore.utils import getToolByName
        types = getToolByName(self.portal, 'portal_types')
        self.assertNotEqual(types.getTypeInfo('library'), None)
        self.assertNotEqual(types.getTypeInfo('library_folder'), None)
        self.assertNotEqual(types.getTypeInfo('library_folder_proxy'), None)

    def test_workflows_added(self):
        from Products.CMFCore.utils import getToolByName
        workflow = getToolByName(self.portal, 'portal_workflow')
        self.assertNotEqual(workflow.getWorkflowById('library_workflow'), None)
        self.assertNotEqual(workflow.getWorkflowById('library_proxy_workflow'),
                            None)

    def test_role_added(self):
        self.assertTrue('Manager' in self.portal.valid_roles())

    def test_permissions_added(self):
        permission = 'collective.library: Add library'
        roles = [r['name'] for r in self.portal.rolesOfPermission(permission)
                 if r['selected']]
        self.assertEqual(roles, ['Contributor',
                                 'Manager',
                                 'Owner',
                                 'Site Administrator'])
        permission = 'collective.library: Add library folder'
        roles = [r['name'] for r in self.portal.rolesOfPermission(permission)
                 if r['selected']]
        self.assertEqual(roles, ['Contributor',
                                 'Manager',
                                 'Owner',
                                 'Site Administrator'])


class TestUninstall(BaseTestCase):

    def setUp(self):
        super(TestUninstall, self).setUp()
        from Products.CMFCore.utils import getToolByName
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProducts(['collective.library'])
        installer.uninstallProducts(['collective.library'])

    def test_product_uninstalled(self):
        from Products.CMFCore.utils import getToolByName
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertFalse(installer.isProductInstalled('collective.library'))

    def test_indexes_removed(self):
        from Products.CMFCore.utils import getToolByName
        catalog = getToolByName(self.portal, 'portal_catalog')
        with self.assertRaises(KeyError):
            catalog._catalog.getIndex('parent_libraries')

    def test_types_removed(self):
        from Products.CMFCore.utils import getToolByName
        types = getToolByName(self.portal, 'portal_types')
        self.assertEqual(types.getTypeInfo('library'), None)
        self.assertEqual(types.getTypeInfo('library_folder'), None)
        self.assertEqual(types.getTypeInfo('library_folder_proxy'), None)

    def test_workflows_removed(self):
        from Products.CMFCore.utils import getToolByName
        workflow = getToolByName(self.portal, 'portal_workflow')
        self.assertEqual(workflow.getWorkflowById('library_workflow'), None)
        self.assertEqual(workflow.getWorkflowById('library_proxy_workflow'),
                         None)
