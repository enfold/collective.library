
from . import constants
from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.api import content as content_api
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def base_getattr(obj, attr, default=None):
    return getattr(aq_base(obj), attr, default)


def get_ancestor(obj, portal_type):
    parent_type = base_getattr(obj, 'portal_type', '')
    if parent_type == portal_type:
        return obj
    if (portal_type == constants.LIBRARY_FOLDER_PORTAL_TYPE
            and parent_type == constants.LIBRARY_PORTAL_TYPE):
        return None
    for parent in aq_chain(aq_inner(obj))[1:]:
        parent_type = base_getattr(parent, 'portal_type', '')
        if parent_type not in (constants.LIBRARY_PORTAL_TYPE,
                               constants.LIBRARY_FOLDER_PORTAL_TYPE,
                               constants.LIBRARY_FOLDER_PROXY_PORTAL_TYPE):
            break
        if parent_type == portal_type:
            return parent
        if (portal_type == constants.LIBRARY_FOLDER_PORTAL_TYPE
                and parent_type == constants.LIBRARY_PORTAL_TYPE):
            break
    return None


def get_library(obj):
    return get_ancestor(obj, constants.LIBRARY_PORTAL_TYPE)


def get_library_folder(obj):
    return get_ancestor(obj, constants.LIBRARY_FOLDER_PORTAL_TYPE)


def get_parent_libraries(obj, uids=False):
    library = get_library(obj)
    libraries = list()
    seen = dict()

    def get_parents(lib):
        if lib is None:
            return
        uid = content_api.get_uuid(lib)
        if uid not in seen:
            seen[uid] = True
            if uids:
                libraries.append(uid)
            else:
                libraries.append(lib)
            relations = base_getattr(lib, constants.PARENT_LIBRARIES_ATTRIBUTE,
                                     list())
            for relation in relations:
                get_parents(relation.to_object)

    get_parents(library)
    libraries.reverse()
    return libraries


def get_path_in_library(obj):
    if obj.portal_type == constants.LIBRARY_PORTAL_TYPE:
        return None
    library = get_library(obj)
    if library is not None:
        obj_path = obj.getPhysicalPath()
        library_path = library.getPhysicalPath()
        path_in_library = ['']
        path_in_library.extend(obj_path[len(library_path):])
        return tuple(path_in_library)


def get_child_libraries(library):
    libraries = list()
    relation_catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    seen = dict()

    def get_children(lib):
        lib_id = intids.queryId(lib)
        if lib_id is None:
            return
        query = {'to_id': lib_id,
                 'from_attribute': constants.PARENT_LIBRARIES_ATTRIBUTE}
        for relation in relation_catalog.findRelations(query):
            child = relation.from_object
            if child is None:
                continue
            uid = content_api.get_uuid(child)
            if uid not in seen:
                seen[uid] = True
                libraries.append(child)
                get_children(child)
    get_children(library)
    return libraries
