from downloaders import BaseDownloader
from sources.base import BaseSource

class MediaSource(BaseSource):
    name = "media"

    downloadable = True
    watchable = True

    def __init__(self,url,headers,filename):
        self.url = url
        self.headers = headers
        self.filename = filename

    def download(self,downloader:BaseDownloader,saveroute,**kwargs):
        downloader.download(self.url,saveroute,self.filename,headers = self.headers,**kwargs)