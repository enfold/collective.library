# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.content import DocumentBylineViewlet \
    as BaseDocumentBylineViewlet


class DocumentBylineViewlet(BaseDocumentBylineViewlet):
    """ collective.library folder proxy byline viewlet """

    def show(self):
        return False
