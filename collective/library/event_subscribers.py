
from plone.api import content as content_api
from plone.api import portal as portal_api
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component.interfaces import IFactory
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.container.interfaces import IContainerModifiedEvent

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
