# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.content import DocumentBylineViewlet \
    as BaseDocumentBylineViewlet


class DocumentBylineViewlet(BaseDocumentBylineViewlet):

    def show(self):
        return False
