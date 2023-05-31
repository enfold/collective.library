
from . import utils as library_utils
from Products.CMFCore.interfaces import IContentish
from plone.api import content as content_api
from plone.indexer.decorator import indexer


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
    library = library_utils.get_library(obj)
    if library is not None:
        return content_api.get_uuid(library)
