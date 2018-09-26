
from collective.library.vocabularies import LibrarySource
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import Interface


class ILibraryContent(Interface):
    """"""


class ILibrary(ILibraryContent):
    """"""

    parent_libraries = RelationList(
        title=u'Parent Libraries',
        default=list(),
        value_type=RelationChoice(source=LibrarySource()),
        required=False)


class ILibraryFolder(ILibraryContent):
    """"""


class ILibraryFolderProxy(ILibraryContent):
    """"""
