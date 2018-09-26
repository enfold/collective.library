
from . import constants
from plone.app.vocabularies.catalog import CatalogSource
from zope.component import queryAdapter
from zope.interface import Interface
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder


class ILibraryQuery(Interface):
    """"""


class LibrarySource(object):
    """"""
    implements(IContextSourceBinder)

    def __init__(self, **query):
        self.query = query

    def __call__(self, context):
        query = self.query.copy()
        query['portal_type'] = constants.LIBRARY_PORTAL_TYPE
        query_factory = queryAdapter(context, interface=ILibraryQuery)
        if query_factory is not None:
            query.update(query_factory())
        return CatalogSource(**query)
