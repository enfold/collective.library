
from .constants import LIBRARY_PORTAL_TYPE
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import Interface


class ILibraryContent(Interface):
    """"""


class ILibrary(ILibraryContent):
    """"""

    parent_libraries = RelationList(
        title=u'Parent Libraries',
        default=list(),
        value_type=RelationChoice(vocabulary='plone.app.vocabularies.Catalog'),
        required=False)
    form.widget(
        'parent_libraries',
        RelatedItemsFieldWidget,
        vocabulary='plone.app.vocabularies.Catalog',
        pattern_options={
            'selectableTypes': [LIBRARY_PORTAL_TYPE],
        },
    )


class ILibraryFolder(ILibraryContent):
    """"""


class ILibraryFolderProxy(ILibraryContent):
    """"""


class ILibraryAdditionalQuery(Interface):
    """"""
