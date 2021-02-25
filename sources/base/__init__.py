from typing import List


class CommonSource():
    name = None

    @classmethod
    def getSourceName(cls):
        return cls.name

    @classmethod
    def initFromUrl(cls,url):
        pass

    @property
    def info(self):
        return {}

    def getBaseSources(self):
        return {}

    def load(self):
        pass

    @classmethod
    def applicable(cls, url):
        return False

class BaseSource():
    name = None

    def __init__(self):
        self.url = ""
        self.headers = {}
        self.filename = ""

    @classmethod
    def getSourceName(cls):
        return "base.%s" % cls.name

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