from abc import ABCMeta,abstractmethod,abstractproperty
from typing import Dict

from sources.base.SearchResult import SearchResults


class BaseInterface(metaclass=ABCMeta):
    pass

class DownloadableSource(BaseInterface):
    @abstractmethod
    def download(self, downloader, saveroute, **kwargs):
        pass

    @property
    @abstractmethod
    def suffix(self):
        pass

class SearchableSource(BaseInterface):

    @classmethod
    @abstractmethod
    def search(cls, keyword,*args, **kwargs) -> SearchResults:
        pass

class WatchableSource(BaseInterface):
    pass