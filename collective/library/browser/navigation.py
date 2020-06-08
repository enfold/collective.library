# -*- coding: utf-8 -*-

from ..interfaces import ILibraryContent
from Acquisition import aq_parent
from Products.CMFPlone import utils as plone_utils
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import implementer


class INavigationPortlet(IPortletDataProvider):
    """ A navigation portlet for the library types """


@implementer(INavigationPortlet)
class Assignment(base.Assignment):
    """ collective.library navigation portlet assignment override """

    title = u'Navigation'


class Renderer(base.Renderer):
    """ collective.library navigation portlet renderer override """

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        #import pdb;pdb.set_trace()
        if ILibraryContent.providedBy(context):
            folder = context
        else:
            parent = aq_parent(context)
            if ILibraryContent.providedBy(parent):
                folder = parent
            else:
                folder = None

        if folder is None:
            self.contents = list()
            self.base_url = ''
        else:
            self.contents = folder.get_content(objects=False, folders_only=True)
            self.base_url = folder.absolute_url()

    @property
    def available(self):
        return len(self.contents) != 0

    def get_items(self):
        items = list()
        base_url = self.base_url
        idnormalizer = getUtility(IIDNormalizer)
        for item in self.contents:
            current = True
            in_path = True
            id = item.getId
            normalized_id = idnormalizer.normalize(id)
            portal_type = getattr(item, 'portal_type', None)
            review_state = getattr(item, 'review_state', None)
            normalized_review_state = idnormalizer.normalize(review_state)
            normalized_portal_type = idnormalizer.normalize(portal_type)
            context_path = '/'.join(self.context.getPhysicalPath())
            item_path = item.getPath()
            items.append(
                {
                    'url': '%s/%s' % (base_url, item.getId),
                    'description': item.Description,
                    'title': plone_utils.pretty_title_or_id(self.context, item),
                    'current': current,
                    'in_path': in_path,
                    'normalized_id': normalized_id,
                    'normalized_review_state': normalized_review_state,
                    'normalized_portal_type': normalized_portal_type,
                    'local_content': item_path.startswith(context_path),
                }
            )
        return items

    render = ViewPageTemplateFile('navigation.pt')


class AddForm(base.NullAddForm):
    """ collective.library navigation portlet add form override """

    def create(self):
        return Assignment()
