from sources.base.interface import DownloadableSource
from utils import file

from downloaders import BaseDownloader
from sources.base import BaseSource


class TextSource(BaseSource,DownloadableSource):
    name = "text"

    def __init__(self, url, headers, filename,filecontent):
        self.url = url
        self.headers = headers
        self.filename = filename
        self.filecontent = filecontent

    @property
    def suffix(self):
        return self.filename.split(".")[-1]

    def download(self, downloader: BaseDownloader, saveroute, **kwargs):
        if (self.url == ""):
            file.writeToFile(self.filecontent,saveroute,self.filename)
        else:
            downloader.download(self.url, saveroute, self.filename, headers = self.headers,**kwargs)