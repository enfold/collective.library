from .base import BaseTestCase


class TestLibrary(BaseTestCase):

    def setUp(self):
        super(TestLibrary, self).setUp()
        self.login_as_portal_owner()

    def test_add_library(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        self.assertEqual(self.portal['lib1'].Title(), u'A library')

    def test_add_content_to_library(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        for ctype in ['File', 'Image', 'Event', 'Collection', 'Document',
                      'Link', 'News Item']:
            lib1.invokeFactory(ctype, ctype,
                               title=u'A library {}'.format(ctype))
            self.assertTrue(ctype in lib1)
            self.assertEqual(lib1[ctype].Title(), u'A library {}'.format(ctype))

    def test_list_library_contents(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        for ctype in ['File', 'Image', 'Event', 'Collection', 'Document',
                      'Link', 'News Item']:
            lib1.invokeFactory(ctype, ctype,
                               title=u'A library {}'.format(ctype))
        self.assertEqual(lib1.listFolderContents(), [lib1['Collection'],
                                                     lib1['Document'],
                                                     lib1['Event'],
                                                     lib1['File'],
                                                     lib1['Image'],
                                                     lib1['Link'],
                                                     lib1['News Item'],
                                                     ])

    def test_regular_folder_not_addable(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        with self.assertRaises(ValueError):
            lib1.invokeFactory('Folder', 'folder1', title=u'A folder')

    def test_remove_content_from_library(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('Document', 'page1',
                           title=u'A library page')
        self.assertTrue('page1' in lib1)
        self.assertEqual(lib1['page1'].Title(), u'A library page')
        lib1.manage_delObjects(['page1'])
        self.assertTrue('page1' not in lib1)

    def test_add_library_folder(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'libfolder1',
                           title=u'A library folder')
        self.assertTrue('libfolder1' in lib1)
        self.assertEqual(lib1['libfolder1'].Title(), u'A library folder')

    def test_add_content_to_library_folder(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'libfolder1',
                           title=u'A library folder')
        folder1 = lib1['libfolder1']
        for ctype in ['File', 'Image', 'Event', 'Collection', 'Document',
                      'Link', 'News Item']:
            folder1.invokeFactory(ctype, ctype,
                                  title=u'A library {}'.format(ctype))
            self.assertTrue(ctype in folder1)
            self.assertEqual(folder1[ctype].Title(),
                             u'A library {}'.format(ctype))

    def test_list_library_folder_contents(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'libfolder1',
                           title=u'A library folder')
        folder1 = lib1['libfolder1']
        for ctype in ['File', 'Image', 'Event', 'Collection', 'Document',
                      'Link', 'News Item']:
            folder1.invokeFactory(ctype, ctype,
                                  title=u'A library {}'.format(ctype))
        self.assertEqual(folder1.listFolderContents(), [folder1['Collection'],
                                                        folder1['Document'],
                                                        folder1['Event'],
                                                        folder1['File'],
                                                        folder1['Image'],
                                                        folder1['Link'],
                                                        folder1['News Item'],
                                                        ])

    def test_remove_content_from_library_folder(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'libfolder1',
                           title=u'A library folder')
        folder1 = lib1['libfolder1']
        folder1.invokeFactory('Document', 'page1',
                              title=u'A library page')
        self.assertTrue('page1' in folder1)
        self.assertEqual(folder1['page1'].Title(), u'A library page')
        folder1.manage_delObjects(['page1'])
        self.assertTrue('page1' not in folder1)

    def test_add_library_folder_to_library_folder(self):
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'libfolder1',
                           title=u'A library folder')
        self.assertTrue('libfolder1' in lib1)
        self.assertEqual(lib1['libfolder1'].Title(), u'A library folder')
        folder1 = lib1['libfolder1']
        folder1.invokeFactory('library_folder', 'libfolder2',
                              title=u'Another library folder')
        self.assertTrue('libfolder2' in folder1)
        self.assertEqual(folder1['libfolder2'].Title(),
                         u'Another library folder')

    def test_library_folder_not_addable_globally(self):
        with self.assertRaises(ValueError):
            self.portal.invokeFactory('library_folder', 'libfolder1',
                                      title=u'A library folder')

    def test_library_folder_proxy_not_addable(self):
        from AccessControl import Unauthorized
        self.portal.invokeFactory('library', 'lib1', title=u'A library')
        lib1 = self.portal['lib1']
        with self.assertRaises(Unauthorized):
            lib1.invokeFactory('library_folder_proxy', 'libfolder1',
                               title=u'A library folder proxy')


class TestParentLibraries(BaseTestCase):

    def setUp(self):
        super(TestParentLibraries, self).setUp()
        from zope.component import getUtility
        from zope.intid.interfaces import IIntIds
        from z3c.relationfield import RelationValue
        self.intids = getUtility(IIntIds)
        self.login_as_portal_owner()
        self.portal.invokeFactory('library', 'lib1', title=u'library 1')
        lib1 = self.portal['lib1']
        lib1.invokeFactory('library_folder', 'folder1',
                           title=u'library folder 1')
        lib1.invokeFactory('library_folder', 'folder2',
                           title=u'library folder 2')
        lib1.invokeFactory('Document', 'document1', title=u'document 1')
        folder1 = lib1['folder1']
        folder1.invokeFactory('File', 'file1', title=u'file 1')
        folder2 = lib1['folder2']
        folder2.invokeFactory('library_folder', 'folder4',
                              title=u'library folder 4')
        lib1_id = self.intids.getId(lib1)
        lib1_rel = RelationValue(lib1_id)
        self.portal.invokeFactory('library', 'lib2', title=u'library 2',
                                  parent_libraries=[lib1_rel])
        lib2 = self.portal['lib2']
        lib2.invokeFactory('library_folder', 'folder3',
                           title=u'library folder 3')
        folder3 = lib2['folder3']
        folder3.invokeFactory('Collection', 'collection1',
                              title=u'collection 1')
        lib2_id = self.intids.getId(lib2)
        lib2_rel = RelationValue(lib2_id)
        self.portal.invokeFactory('library', 'lib3', title=u'library 3',
                                  parent_libraries=[lib2_rel])
        lib3 = self.portal['lib3']
        lib3.invokeFactory('News Item', 'newsitem1', title=u'news item 1')
        self.portal.invokeFactory('library', 'lib4', title=u'library 4',
                                  parent_libraries=[lib1_rel])
        lib4 = self.portal['lib4']
        lib4.invokeFactory('library_folder', 'folder5',
                           title=u'library folder 5')
        folder5 = lib4['folder5']
        folder5.invokeFactory('Image', 'image1', title=u'image 1')
        lib4_id = self.intids.getId(lib4)
        lib4_rel = RelationValue(lib4_id)
        self.portal.invokeFactory('library', 'lib5', title=u'library 5',
                                  parent_libraries=[lib4_rel])
        lib5 = self.portal['lib5']
        lib5.invokeFactory('library_folder', 'folder6',
                           title=u'library folder 6')
        folder6 = lib5['folder6']
        folder6.invokeFactory('Event', 'event1', title=u'event 1')
        lib5_id = self.intids.getId(lib5)
        lib5_rel = RelationValue(lib5_id)
        self.portal.invokeFactory('library', 'lib6', title=u'library 6',
                                  parent_libraries=[lib2_rel, lib5_rel])

    def test_library1_folder_contents(self):
        lib1 = self.portal['lib1']
        expected_contents = [lib1['folder1'],
                             lib1['folder2'],
                             lib1['document1']
                             ]
        self.assertListEqual(lib1.get_content(), expected_contents)

    def test_library2_folder_contents(self):
        lib2 = self.portal['lib2']
        expected_contents = ['folder1',
                             'folder3',
                             'document1']
        content_ids = [c.id for c in lib2.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_library3_folder_contents(self):
        lib3 = self.portal['lib3']
        expected_contents = ['folder1',
                             'folder3',
                             'document1',
                             'newsitem1']
        content_ids = [c.id for c in lib3.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_library4_folder_contents(self):
        lib4 = self.portal['lib4']
        expected_contents = ['folder1',
                             'folder5',
                             'document1']
        content_ids = [c.id for c in lib4.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_library5_folder_contents(self):
        lib5 = self.portal['lib5']
        expected_contents = ['folder1',
                             'folder5',
                             'folder6',
                             'document1']
        content_ids = [c.id for c in lib5.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_library6_folder_contents(self):
        lib6 = self.portal['lib6']
        expected_contents = ['folder1',
                             'folder3',
                             'folder5',
                             'folder6',
                             'document1']
        content_ids = [c.id for c in lib6.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_change_parent_libraries(self):
        from z3c.relationfield import RelationValue
        lib1 = self.portal['lib1']
        lib1_id = self.intids.getId(lib1)
        lib1_rel = RelationValue(lib1_id)
        lib6 = self.portal['lib6']
        lib6.parent_libraries = [lib1_rel]
        expected_contents = ['folder1',
                             'document1']
        content_ids = [c.id for c in lib6.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_list_proxied_folder_contents(self):
        lib5 = self.portal['lib5']
        proxied = lib5['folder5']
        expected_contents = ['image1']
        content_ids = [c.id for c in proxied.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_add_content_to_parent_library(self):
        lib4 = self.portal['lib4']
        folder5 = lib4['folder5']
        folder5.invokeFactory('Document', 'document2', title=u'document 2')
        lib5 = self.portal['lib5']
        proxied = lib5['folder5']
        expected_contents = ['document2',
                             'image1']
        content_ids = [c.id for c in proxied.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_add_content_to_proxied_folder(self):
        lib5 = self.portal['lib5']
        proxied = lib5['folder5']
        proxied.invokeFactory('Document', 'document2', title=u'document 2')
        expected_contents = ['document2',
                             'image1']
        content_ids = [c.id for c in proxied.get_content()]
        self.assertListEqual(content_ids, expected_contents)
        lib4 = self.portal['lib4']
        folder5 = lib4['folder5']
        expected_contents = ['image1']
        content_ids = [c.id for c in folder5.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_add_folder_to_parent_library(self):
        lib4 = self.portal['lib4']
        folder5 = lib4['folder5']
        folder5.invokeFactory('library_folder', 'folder7',
                              title=u'library folder 7')
        folder7 = folder5['folder7']
        folder7.invokeFactory('Document', 'document2', title=u'document 2')
        lib5 = self.portal['lib5']
        proxied = lib5['folder5']['folder7']
        expected_contents = ['document2']
        content_ids = [c.id for c in proxied.get_content()]
        self.assertListEqual(content_ids, expected_contents)

    def test_delete_content_from_parent_folder(self):
        from AccessControl import Unauthorized
        lib2 = self.portal['lib2']
        proxied = lib2['folder1']
        with self.assertRaises(Unauthorized):
            proxied.manage_delObjects(['document1'])

    def test_library_propfind(self):
        lib1 = self.portal['lib1']
        propfind = lib1.PROPFIND(self.request, self.request.response)
        self.assertEquals(propfind.status, 207)
        self.assertIn('<n:title>library 1</n:title>', propfind.body)
        self.assertIn('<n:title>library folder 1</n:title>', propfind.body)
        self.assertIn('<n:title>library folder 2</n:title>', propfind.body)
        self.assertIn('<n:title>library folder 4</n:title>', propfind.body)
        self.assertIn('<n:title>document 1</n:title>', propfind.body)
