from Acquisition import aq_inner
from zope.interface import implementer

from plone.app.layout.globals.context import ContextState as PloneContextState
from plone.app.layout.globals.interfaces import IContextState
from plone.memoize.view import memoize


implementer(IContextState)
class ContextState(PloneContextState):

    @property
    def is_content_proxy(self):
        context = aq_inner(self.context)
        return getattr(context, 'is_content_proxy', False)

    @property
    def is_folder_proxy(self):
        context = aq_inner(self.context)
        return getattr(context, 'is_folder_proxy', False)

    @memoize
    def actions(self, category=None, max=-1):
        result = super(ContextState, self).actions(category, max)
        # remove edit action
        if self.is_content_proxy or self.is_folder_proxy:
            result = [action for action in result if action['id'] != 'edit']
        # no object buttons for content proxy
        if self.is_content_proxy:
            result = [action for action in result
                      if action['category'] != 'object_buttons']
        # no object buttons except paste for folder proxy
        if self.is_folder_proxy:
            result = [action for action in result
                      if action['category'] != 'object_buttons' and action['id'] != 'paste']
        return result
