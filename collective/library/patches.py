import logging
from Acquisition import aq_inner
from plone.app.content.browser import contents
from plone.app.uuid.utils import uuidToCatalogBrain
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

logger = logging.getLogger(__name__)

OriginalContentsBaseAction = contents.ContentsBaseAction


class LibraryContentsBaseAction(OriginalContentsBaseAction):

    def __call__(self, keep_selection_order=False):
        self.protect()
        self.errors = []
        context = aq_inner(self.context)
        selection = self.get_selection()

        parts = str(self.request.form.get('folder', '').lstrip('/')).split('/')
        if parts:
            parent = self.site.unrestrictedTraverse('/'.join(parts[:-1]))
            self.dest = parent.restrictedTraverse(parts[-1])

        self.catalog = getToolByName(context, 'portal_catalog')
        self.mtool = getToolByName(self.context, 'portal_membership')

        brains = []
        if keep_selection_order:
            brains = [uuidToCatalogBrain(uid) for uid in selection]
        else:
            brains = self.catalog(UID=selection, show_inactive=True)

        for brain in brains:
            if not brain:
                continue
            # remove everyone so we know if we missed any
            selection.remove(brain.UID)
            obj = brain.getObject()
            if (
                self.required_obj_permission
                and not self.mtool.checkPermission(
                    self.required_obj_permission,
                    obj
                )
            ):
                self.errors.append(_(
                    'Permission denied for "${title}"',
                    mapping={'title': self.objectTitle(obj)}
                ))
                continue
            obj_id = brain.getId
            from_obj = parent
            if parts:
                from_obj = self.dest
            try:
                traversed_obj = from_obj.restrictedTraverse(obj_id)
            except KeyError:
                traversed_obj = None
            if traversed_obj is not None:
                is_content_proxy = getattr(traversed_obj, 'is_content_proxy', False)
                is_folder_proxy = getattr(traversed_obj, 'is_folder_proxy', False)
                if is_content_proxy or is_folder_proxy:
                    self.errors.append(_(
                        'Invalid operation for "${title}"',
                        mapping={'title': self.objectTitle(traversed_obj)}
                    ))
                    continue
            self.action(obj)

        self.finish()
        return self.message(selection)

# plone.app.content.browser.contents.ContentsBaseAction is patched to prevent
# actions on proxied content
contents.ContentsBaseAction = LibraryContentsBaseAction
logger.warn('Patched plone.app.content.browser.contents.ContentsBaseAction')
