
from AccessControl.Permission import addPermission
from AccessControl.SecurityInfo import ModuleSecurityInfo


security = ModuleSecurityInfo()

security.declarePublic('AddLibrary')
AddLibrary = 'collective.library: Add library'
addPermission(AddLibrary, ('Manager', 'Owner'))

security.declarePublic('AddLibraryFolder')
AddLibraryFolder = 'collective.library: Add library folder'
addPermission(AddLibraryFolder, ('Manager', 'Owner'))

security.declarePublic('AddLibraryFolderProxy')
AddLibraryFolderProxy = 'collective.library: Add library folder proxy'
addPermission(AddLibraryFolderProxy, ())
