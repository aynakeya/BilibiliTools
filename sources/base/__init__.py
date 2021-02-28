import traceback
from typing import List
from functools import wraps

class CommonSourceWrapper():
    @staticmethod
    def handleException(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                return None
        return wrapper

class CommonSource():
    __source_name__ = None
    wrapper = CommonSourceWrapper

    @classmethod
    def getSourceName(cls):
        return cls.__source_name__

    @classmethod
    def initFromUrl(cls,url):
        pass

    @property
    def info(self):
        return {}

    def getBaseSources(self,*args,**kwargs):
        return {}

    @CommonSourceWrapper.handleException
    def load(self,*args,**kwargs):
        pass

    @classmethod
    def applicable(cls, url):
        return False

class BaseSource():
    __source_name__ = None

    def __init__(self):
        self.url = ""
        self.headers = {}
        self.filename = ""

    @classmethod
    def getSourceName(cls):
        return "base.%s" % cls.__source_name__

class SourceSelector():
    def __init__(self,*args):
        self.sources = args
        self.sources: List[CommonSource]

    def select(self,url):
        for source in self.sources:
            if source.applicable(url):
                return source
        return None

    def getSourceNames(self):
        return [s.getSourceName() for s in self.sources]

    def getByName(self,name):
        for source in self.sources:
            source:CommonSource
            if source.getSourceName() == name:
                return source
        return None

from .Media import MediaSource
from .Picture import PictureSource
from .Text import TextSource
from .SearchResult import SearchResult,SearchResults