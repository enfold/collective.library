
from . import constants
from . import utils as library_utils
from .interfaces import ILibrary
from .interfaces import ILibraryAdditionalQuery
from .interfaces import ILibraryFolder
from .interfaces import ILibraryFolderProxy
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import webdav_access
from AccessControl import Permissions as acpermissions
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore import permissions as cmf_permissions
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.interfaces import IConstrainTypes
from ZPublisher.interfaces import UseTraversalDefault
from plone.api import content as content_api
from plone.api import portal as portal_api
from plone.app.iterate.interfaces import IIterateAware
from plone.dexterity.content import AttributeValidator
from plone.dexterity.content import FTIAwareSpecification
from plone.dexterity.content import DexterityContent
from plone.dexterity.content import PasteBehaviourMixin
from plone.dexterity.filerepresentation import DAVCollectionMixin
from plone.dexterity.interfaces import IDexterityContainer
from webdav.davcmds import PropFind
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface.declarations import implementedBy
from zope.interface.declarations import providedBy
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor

try:
    from plone.multilingual.interfaces import ITranslatable
except ImportError:
    ITranslatable = None

import new
import six
import types

_marker = object()


@implementer(IDexterityContainer)
class BaseLibraryContainer(PasteBehaviourMixin, DAVCollectionMixin,
                           BrowserDefaultMixin, CMFCatalogAware,
                           BTreeFolder2Base, PortalFolderBase,
                           DexterityContent):
    """ """

    __providedBy__ = FTIAwareSpecification()
    __allow_access_to_unprotected_subobjects__ = AttributeValidator()

    __dav_collection__ = 1

    security = ClassSecurityInfo()
    security.declareProtected(
        acpermissions.copy_or_move, 'manage_copyObjects')
    security.declareProtected(
        cmf_permissions.ModifyPortalContent, 'manage_cutObjects')
    security.declareProtected(
        cmf_permissions.ModifyPortalContent, 'manage_pasteObjects')
    security.declareProtected(
        cmf_permissions.ModifyPortalContent, 'manage_renameObject')
    security.declareProtected(
        cmf_permissions.ModifyPortalContent, 'manage_renameObjects')

    isPrincipiaFolderish = 1

    # make sure CMFCatalogAware's manage_options don't take precedence
    manage_options = PortalFolderBase.manage_options

    # Make sure PortalFolder's accessors and mutators don't take precedence
    Title = DexterityContent.Title
    setTitle = DexterityContent.setTitle
    Description = DexterityContent.Description
    setDescription = DexterityContent.setDescription

    def __init__(self, id=None, **kwargs):
        PortalFolderBase.__init__(self, id)
        BTreeFolder2Base.__init__(self, id)
        DexterityContent.__init__(self, id, **kwargs)

    def _checkId(self, id, allow_dup=0):
        content = self.get_content(name=id)
        if len(content):
            if ILibraryFolderProxy.providedBy(content[0]):
                return
        PortalFolderBase._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

    def _getOb(self, name, default=_marker):
        ob = super(BaseLibraryContainer, self)._getOb(name, default=default)
        if ob is default:
            content = self.get_content(name=name)
            if len(content):
                ob = content[0]
            if ob is _marker:
                raise KeyError(name)

        return ob

    def __getattr__(self, name):
        if name.startswith('__') or name == '_v__providedBy__':
            raise AttributeError(name)
        try:
            return DexterityContent.__getattr__(self, name)
        except AttributeError:
            pass

        return BTreeFolder2Base.__getattr__(self, name)

    def get_content(self, name=None, objects=True, restricted=False,
                    folders_only=False, **kw):
        query = {}
        adapter = queryAdapter(self, interface=ILibraryAdditionalQuery)
        if adapter is not None:
            query.update(adapter())
        query.update(kw)
        if 'path' in query:
            del query['path']
        catalog = portal_api.get_tool('portal_catalog')
        portal_types = portal_api.get_tool('portal_types')
        parent_uids = library_utils.get_parent_libraries(self, uids=True)
        library = library_utils.get_library(self)
        if library is None:
            return list()
        library_uid = content_api.get_uuid(library)
        path_in_library = library_utils.get_path_in_library(self)
        if self.portal_type == constants.LIBRARY_PORTAL_TYPE:
            path_in_library = ['']
        if path_in_library is None:
            return list()
        query['path_in_library'] = {'query': '/'.join(path_in_library),
                                    'depth': 1}
        query['library'] = parent_uids

        if folders_only:
            query['portal_type'] = constants.LIBRARY_FOLDER_PORTAL_TYPE
        else:
            query['portal_type'] = [t for t in portal_types.listContentTypes()
                                    if t != constants.LIBRARY_PORTAL_TYPE]

        if 'sort_on' not in query:
            query['sort_on'] = 'sortable_title'
        elif query['sort_on'] == 'getObjPositionInParent':
            query['sort_on'] = 'sortable_title'

        if name is not None:
            query['id'] = name
        content = list()
        if restricted:
            results = catalog.searchResults(**query)
        else:
            results = catalog.unrestrictedSearchResults(**query)
        seen = dict()
        count = 0
        for brain in results:
            if objects:
                if (brain.portal_type == constants.LIBRARY_FOLDER_PORTAL_TYPE
                        and brain.library != library_uid):
                    item = LibraryFolderProxy(id=brain.id,
                                              title=brain.Title).__of__(self)
                else:
                    if restricted:
                        item = brain.getObject()
                    else:
                        item = brain._unrestrictedGetObject()
                    item = ContentProxy(item).__of__(self)
            else:
                item = brain
            _id = brain.id
            if _id in seen:
                if brain.library == library_uid:
                    content[seen[_id]] = item
            else:
                seen[_id] = count
                content.append(item)
                count = count + 1

        return content

    @security.protected(cmf_permissions.DeleteObjects)
    def manage_delObjects(self, ids=None, REQUEST=None):
        """Delete the contained objects with the specified ids.

        If the current user does not have permission to delete one of the
        objects, an Unauthorized exception will be raised.
        """
        if ids is None:
            ids = []
        if isinstance(ids, six.string_types):
            ids = [ids]
        content_ids = self.contentIds()
        for id in ids:
            # Don't allow delete of objects from parent libraries.
            if id not in content_ids:
                raise Unauthorized(
                    "Do not have permissions to remove this object"
                )
            item = self._getOb(id)
            if not getSecurityManager().checkPermission(
                cmf_permissions.DeleteObjects,
                item
            ):
                raise Unauthorized(
                    "Do not have permissions to remove this object"
                )
        return super(BaseLibraryContainer, self).manage_delObjects(ids, REQUEST=REQUEST)

    # override PortalFolder's allowedContentTypes to respect IConstrainTypes
    # adapters
    def allowedContentTypes(self, context=None):
        if not context:
            context = self

        constrains = IConstrainTypes(context, None)
        if not constrains:
            return super(BaseLibraryContainer, self).allowedContentTypes()

        return constrains.allowedContentTypes()

    # override PortalFolder's invokeFactory to respect IConstrainTypes
    # adapters
    def invokeFactory(self, type_name, id, RESPONSE=None, *args, **kw):
        # Invokes the portal_types tool.
        constrains = IConstrainTypes(self, None)

        if constrains:
            # Do permission check before constrain checking so we'll get
            # an Unauthorized over a ValueError.
            fti = queryUtility(ITypeInformation, name=type_name)
            if fti is not None and not fti.isConstructionAllowed(self):
                raise Unauthorized('Cannot create %s' % fti.getId())

            allowed_ids = [i.getId() for i in constrains.allowedContentTypes()]
            if type_name not in allowed_ids:
                raise ValueError(
                    'Subobject type disallowed by IConstrainTypes adapter: %s'
                    % type_name
                )

        return super(BaseLibraryContainer, self).invokeFactory(
            type_name, id, RESPONSE, *args, **kw
        )

    def __bobo_traverse__(self, REQUEST, name):
        ob = self._getOb(name, default=None)
        if ob is not None:
            return ob
        raise UseTraversalDefault

    @security.protected(cmf_permissions.ListFolderContents)
    def listDAVObjects(self):
        """ """
        return list(self.get_content())

    @security.protected(webdav_access)
    def PROPFIND(self, REQUEST, RESPONSE):
        """ """
        self.dav__init(REQUEST, RESPONSE)
        cmd = PropFind(REQUEST)
        result = cmd.apply(self)
        # work around MSIE DAV bug for creation and modified date
        if (REQUEST.get_header('User-Agent') ==
            'Microsoft Data Access Internet Publishing Provider DAV 1.1'):
            result = result.replace('<n:getlastmodified xmlns:n="DAV:">',
                                    '<n:getlastmodified xmlns:n="DAV:" xmlns:b="urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/" b:dt="dateTime.rfc1123">')
            result = result.replace('<n:creationdate xmlns:n="DAV:">',
                                    '<n:creationdate xmlns:n="DAV:" xmlns:b="urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/" b:dt="dateTime.tz">')
        RESPONSE.setStatus(207)
        RESPONSE.setHeader('Content-Type', 'text/xml; charset="utf-8"')
        RESPONSE.setBody(result)
        return RESPONSE


@implementer(ILibrary)
class Library(BaseLibraryContainer):
    """ """

    security = ClassSecurityInfo()


InitializeClass(Library)


@implementer(ILibraryFolder)
class LibraryFolder(BaseLibraryContainer):
    """ """

    security = ClassSecurityInfo()


InitializeClass(LibraryFolder)


@implementer(ILibraryFolderProxy)
class LibraryFolderProxy(BaseLibraryContainer):
    """ """

    security = ClassSecurityInfo()

    portal_type = 'library_folder_proxy'

    def _setObject(self, id, object, roles=None, user=None, set_owner=1,
                   suppress_events=False):
        nearest_folder = library_utils.get_library_folder(self)
        path_in_library = library_utils.get_path_in_library(self)
        if nearest_folder is not None:
            nearest_folder_path = library_utils.get_path_in_library(
                nearest_folder)
            path_in_folder = path_in_library[len(nearest_folder_path):]
            parent = nearest_folder
        else:
            path_in_folder = path_in_library[1:]
            parent = library_utils.get_library(self)

        for name in path_in_folder:
            brain = parent.get_content(name=name, objects=False)[0]
            parent = content_api.create(
                container=parent,
                type=constants.LIBRARY_FOLDER_PORTAL_TYPE,
                id=name,
                title=brain.Title)
        return parent._setObject(id, object, roles=roles, user=user,
                                 set_owner=set_owner,
                                 suppress_events=suppress_events)


InitializeClass(LibraryFolderProxy)


class DelegatingSpecification(ObjectSpecificationDescriptor):
    """A __providedBy__ decorator that returns the interfaces provided by
    the object, plus those of the cached object.
    """

    def __get__(self, inst, cls=None):

        # We're looking at a class - fall back on default
        if inst is None:
            return getObjectSpecification(cls)

        # Find the cached value.
        cache = getattr(inst, '_v__providedBy__', None)

        # Find the data we need to know if our cache needs to be invalidated
        provided = alias_provides = getattr(inst, '__provides__', None)

        # See if we have a valid cache, and if so return it
        if cache is not None:
            cached_mtime, cached_provides, cached_provided = cache

            if (
                inst._p_mtime == cached_mtime and
                alias_provides is cached_provides
            ):
                return cached_provided

        # If the instance doesn't have a __provides__ attribute, get the
        # interfaces implied by the class as a starting point.
        if provided is None:
            provided = implementedBy(cls)

        # Add the interfaces provided by the target
        target = aq_base(inst._target)
        if target is None:
            return provided  # don't cache yet!

        # Add the interfaces provided by the target, but take away
        # IHasAlias if set
        provided += providedBy(target) - IIterateAware

        if ITranslatable:
            provided -= ITranslatable

        inst._v__providedBy__ = inst._p_mtime, alias_provides, provided
        return provided


class ContentProxy(SimpleItem):

    __providedBy__ = DelegatingSpecification()

    def __init__(self, proxied):
        self._proxied = proxied

    @property
    def id(self):
        return aq_inner(self._proxied).id

    def Title(self):
        """ """
        return self.title

    @property
    def title(self):
        return aq_inner(self._proxied).Title()

    def Description(self):
        """ """
        return aq_inner(self._proxied).Description()

    def __getattr__(self, attr):
        if (
            attr.startswith('_v_')
            or attr.startswith('_p_',)
            or attr.endswith('_Permission')
        ):
            raise AttributeError(attr)

        proxied = aq_inner(self._proxied)

        if not hasattr(aq_base(proxied), attr):
            return super(ContentProxy, self).__getattr__(attr)

        value = getattr(proxied, attr, _marker)

        if value is _marker:
            return super(ContentProxy, self).__getattr__(attr)

        if aq_parent(value) is proxied:
            value = aq_base(value).__of__(self)

        if isinstance(value, types.MethodType):
            return types.MethodType(value.im_func, self, type(self))

        return value

    @property
    def __klass__(self):
        """ """

        klass = getattr(self, '_v_class', None)
        if klass is not None:
            return klass

        proxied = self._proxied

        self._v_class = klass = new.classobj('ContentProxy', (ContentProxy, aq_base(proxied).__class__), {})
        return klass


InitializeClass(ContentProxy)
