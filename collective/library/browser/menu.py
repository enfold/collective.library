from zope.interface import implementer

from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IWorkflowMenu
from plone.app.contentmenu.menu import WorkflowMenu as OriginalWorkflowMenu
from plone.app.contentmenu.menu import ActionsMenu as OriginalActionsMenu


@implementer(IActionsMenu)
class ActionsMenu(OriginalActionsMenu):

    def getMenuItems(self, context, request):
        items = super(ActionsMenu, self).getMenuItems(context, request)
        is_content_proxy = getattr(context, 'is_content_proxy', False)
        is_folder_proxy = getattr(context, 'is_folder_proxy', False)
        if is_content_proxy:
            items = []
        if is_folder_proxy:
            items = [item for item in items if item['title'] == 'Paste']
        return items


@implementer(IWorkflowMenu)
class WorkflowMenu(OriginalWorkflowMenu):

    def getMenuItems(self, context, request):
        items = super(WorkflowMenu, self).getMenuItems(context, request)
        is_content_proxy = getattr(context, 'is_content_proxy', False)
        is_folder_proxy = getattr(context, 'is_folder_proxy', False)
        if is_content_proxy or is_folder_proxy:
            items = []
        return items
