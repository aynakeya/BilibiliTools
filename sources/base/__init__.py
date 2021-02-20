class CommonSource():
    name = None

    @classmethod
    def initFromUrl(cls,url):
        pass

    @classmethod
    def getSourceName(cls):
        return cls.name

    @property
    def info(self):
        return None

    def getBaseSources(self):
        return {}

    def load(self):
        pass

    @classmethod
    def applicable(cls, url):
        return False


class BaseSource(CommonSource):
    name = "base"

    downloadable = False
    watchable = False

    def __init__(self):
        self.url = ""
        self.headers = {}
        self.filename = ""

    def getSource(self):
        return "base.%s" % self.name

    def download(self,downloader,saveroute,**kwargs):
        pass

class SourceSelector():
    def __init__(self,*args):
        self.sources = args

    def select(self,url):
        for source in self.sources:
            if source.applicable(url):
                return source
        return None

from .Media import MediaSource
from .Picture import PictureSource
from .Text import TextSource