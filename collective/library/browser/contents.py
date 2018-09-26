
from .. import constants
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Products.Five import BrowserView
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from plone.api import portal as portal_api
from plone.app.content.browser.contents import FolderContentsView as \
    FolderContentsViewBase
from plone.app.content.browser.vocabulary import _parseJSON
from plone.app.content.browser.vocabulary import _safe_callable_metadata
from plone.app.content.browser.vocabulary import _unsafe_metadata
from plone.app.content.browser.vocabulary import DEFAULT_PERMISSION_SECURE
from plone.app.content.utils import json_dumps
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contenttypes.browser.folder import FolderView as BaseFolderView
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.querystring import queryparser

import six


class FolderContentsItemsView(BrowserView):

    def __call__(self, *args, **kwargs):
        context = self.context
        base_url = context.absolute_url()
        parent_path = '/'.join(context.getPhysicalPath())
        self.request.response.setHeader(
            'Content-Type', 'application/json; charset=utf-8'
        )
        query = self.parsed_query()
        results = context.get_content(objects=False, restricted=True, **query)
        total = len(results)

        batch = _parseJSON(self.request.get('batch', ''))
        if batch and ('size' not in batch or 'page' not in batch):
            batch = None  # batching not providing correct options
        if batch:
            # must be slicable for batching support
            page = int(batch['page'])
            size = int(batch['size'])
            if size > 500:
                raise Exception('Max batch size is 500')
            # page is being passed in is 1-based
            start = (max(page - 1, 0)) * size
            end = start + size
            results = results[start:end]

        items = list()
        attributes = _parseJSON(self.request.get('attributes', ''))
        if isinstance(attributes, six.string_types) and attributes:
            attributes = attributes.split(',')

        base_path = self.get_base_path(context)
        sm = getSecurityManager()
        can_edit = sm.checkPermission(DEFAULT_PERMISSION_SECURE, context)
        mtt = portal_api.get_tool('mimetypes_registry')
        for vocab_item in results:
            if vocab_item.portal_type == constants.LIBRARY_PORTAL_TYPE:
                continue
            item = {}
            for attr in attributes:
                key = attr
                if ':' in attr:
                    key, attr = attr.split(':', 1)
                if attr in _unsafe_metadata and not can_edit:
                    continue
                if key == 'path':
                    attr = 'getPath'
                val = getattr(vocab_item, attr, None)
                if callable(val):
                    if attr in _safe_callable_metadata:
                        val = val()
                    else:
                        continue
                if key == 'path':
                    val = '%s/%s' % (parent_path[len(base_path):],
                                     vocab_item['id'])
                if key == 'getURL':
                    val = '%s/%s' % (base_url, vocab_item['id'])
                item[key] = val
                if key == 'getMimeIcon':
                    item[key] = None
                    # get mime type icon url from mimetype registry'
                    contenttype = aq_base(
                        getattr(vocab_item, 'mime_type', None))
                    if contenttype:
                        ctype = mtt.lookup(contenttype)
                        item[key] = '/'.join([
                            base_path,
                            guess_icon_path(ctype[0])])
            items.append(item)

        return json_dumps({
            'results': items,
            'total': total
        })

    def parsed_query(self):
        query = _parseJSON(self.request.get('query', ''))
        if query:
            parsed = queryparser.parseFormquery(
                self.context, query['criteria'])
            if 'sort_on' in query:
                parsed['sort_on'] = query['sort_on']
            if 'sort_order' in query:
                parsed['sort_order'] = str(query['sort_order'])
            query = parsed
        else:
            query = {}
        return query

    def get_base_path(self, context):
        return getNavigationRoot(context)


class FolderContentsView(FolderContentsViewBase):

    def get_options(self):
        options = super(FolderContentsView, self).get_options()
        vocabulary_url = '%s/@@getFolderContentsItems' \
                         % self.context.absolute_url()
        options['vocabularyUrl'] = vocabulary_url
        return options


class FolderListing(BrowserView):

    def __call__(self, batch=False, b_size=20, b_start=0, orphan=0, **kw):
        context = self.context

        results = context.get_content(objects=False, restricted=True, **kw)
        return IContentListing(results)


class FolderView(BaseFolderView):

    def get_url(self, item):
        parent_url = self.context.absolute_url()
        return '%s/%s' % (parent_url, item.id)
