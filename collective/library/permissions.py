
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles


security = ModuleSecurityInfo()

security.declarePublic('AddLibrary')
AddLibrary = 'collective.library: Add library'
setDefaultRoles(AddLibrary, ('Manager', 'Owner'))

security.declarePublic('AddLibraryFolder')
AddLibraryFolder = 'collective.library: Add library folder'
setDefaultRoles(AddLibraryFolder, ('Manager', 'Owner'))

security.declarePublic('AddLibraryFolderProxy')
AddLibraryFolderProxy = 'collective.library: Add library folder proxy'
setDefaultRoles(AddLibraryFolderProxy, ())
