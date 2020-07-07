
from . import constants
from . import utils as library_utils
from plone.api import content as content_api
from plone.api import portal as portal_api
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.annotation.interfaces import IAnnotations
from zope.component.interfaces import IFactory
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent import ObjectMovedEvent

import logging

logger = logging.getLogger(__name__)


def library_modified(obj, event):
    if IContainerModifiedEvent.providedBy(event):
        return
    catalog = portal_api.get_tool('portal_catalog')
    try:
        for brain in catalog.unrestrictedSearchResults(
                parent_libraries=content_api.get_uuid(obj)):
            o = brain._unrestrictedGetObject()
            o.reindexObject(idxs=['parent_libraries'])
    except Exception:
        logger.exception('An error in library_modified event handler')


def library_added(obj, event):
    left_portlet_manager = getUtility(IPortletManager, name='plone.leftcolumn')
    assignable = getMultiAdapter((obj, left_portlet_manager),
                                 ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

    mapping = getMultiAdapter((obj, left_portlet_manager),
                              IPortletAssignmentMapping)
    if 'navigation' not in mapping:
        portlet_factory = getUtility(
            IFactory,
            name='collective.library.portlets.navigation')
        assignment = portlet_factory()
        mapping['navigation'] = assignment


def content_added(obj, event):
    library = library_utils.get_library(obj)
    library_uid = None
    annotations = IAnnotations(obj)
    if library is not None:
        library_uid = content_api.get_uuid(library)
    annotations[constants.LIBRARY_ANNOTATION_KEY] = library_uid


def content_moved(obj, event):
    new_parent = getattr(event, 'newParent', None)
    old_parent = getattr(event, 'oldParent', None)

    if new_parent and old_parent and new_parent != old_parent:
        library = library_utils.get_library(obj)
        annotations = IAnnotations(obj)
        existing_lib_uid = annotations.get(constants.LIBRARY_ANNOTATION_KEY, None)
        modified = False
        if library is not None:
            library_uid = content_api.get_uuid(library)
            if library_uid != existing_lib_uid:
                modified = True
                annotations[constants.LIBRARY_ANNOTATION_KEY] = library_uid

        if existing_lib_uid and library is None:
            modified = True
            annotations[constants.LIBRARY_ANNOTATION_KEY] = None

        if modified:
            obj.reindexObject()
