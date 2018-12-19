
from . import constants
from . import utils as library_utils
from Products.CMFCore.interfaces import IContentish
from plone.indexer.decorator import indexer
from zope.annotation.interfaces import IAnnotations


@indexer(IContentish)
def path_in_library(obj):
    return library_utils.get_path_in_library(obj)


@indexer(IContentish)
def obj_path_in_library(obj):
    path = library_utils.get_path_in_library(obj)
    if path is not None:
        return '/'.join(path)


@indexer(IContentish)
def parent_libraries(obj):
    return library_utils.get_parent_libraries(obj, uids=True)


@indexer(IContentish)
def library(obj):
    annotations = IAnnotations(obj)
    return annotations.get(constants.LIBRARY_ANNOTATION_KEY, None)
