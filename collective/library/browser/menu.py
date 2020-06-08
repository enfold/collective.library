from zope.interface import implementer

from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.interfaces import IWorkflowMenu
from plone.app.contentmenu.interfaces import IWorkflowSubMenuItem
from plone.app.contentmenu.menu import ActionsMenu as OriginalActionsMenu
from plone.app.contentmenu.menu import ActionsSubMenuItem as OriginalActionsSubMenuItem
from plone.app.contentmenu.menu import WorkflowMenu as OriginalWorkflowMenu
from plone.app.contentmenu.menu import WorkflowSubMenuItem as OriginalWorkflowSubMenuItem


@implementer(IActionsMenu)
class ActionsMenu(OriginalActionsMenu):
    """ collective.library actions menu override """

    def getMenuItems(self, context, request):
        items = super(ActionsMenu, self).getMenuItems(context, request)
        is_content_proxy = getattr(context, 'is_content_proxy', False)
        is_folder_proxy = getattr(context, 'is_folder_proxy', False)
        if is_content_proxy:
            items = []
        if is_folder_proxy:
            items = [item for item in items if item['title'] == 'Paste']
        return items


@implementer(IActionsSubMenuItem)
class ActionsSubMenuItem(OriginalActionsSubMenuItem):
    """ collective.library actions submenu item override """

    def available(self):
        result = super(ActionsSubMenuItem, self).available()
        is_content_proxy = getattr(self.context, 'is_content_proxy', False)
        if is_content_proxy:
            result = False
        return result


@implementer(IWorkflowMenu)
class WorkflowMenu(OriginalWorkflowMenu):
    """ collective.library workflow menu override """

    def getMenuItems(self, context, request):
        items = super(WorkflowMenu, self).getMenuItems(context, request)
        is_content_proxy = getattr(context, 'is_content_proxy', False)
        is_folder_proxy = getattr(context, 'is_folder_proxy', False)
        if is_content_proxy or is_folder_proxy:
            items = []
        return items


@implementer(IWorkflowSubMenuItem)
class WorkflowSubMenuItem(OriginalWorkflowSubMenuItem):
    """ collective.library workflow submenu item """

    def available(self):
        result = super(WorkflowSubMenuItem, self).available()
        is_content_proxy = getattr(self.context, 'is_content_proxy', False)
        is_folder_proxy = getattr(self.context, 'is_folder_proxy', False)
        if is_content_proxy or is_folder_proxy:
            result = False
        return result
