from downloaders import BaseDownloader
from sources.base import BaseSource
from sources.base.interface import DownloadableSource, WatchableSource
from utils import formats,file
import os

class MediaSource(BaseSource,DownloadableSource,WatchableSource):
    name = "media"

    def __init__(self,url,headers,filename):
        self.url = url
        self.headers = headers
        self.filename = filename

    @property
    def suffix(self):
        return self.filename.split(".")[-1]

    def download(self,downloader:BaseDownloader,saveroute,**kwargs):
        if (self.suffix == "m3u8"):
            filelist =[]
            newroute = os.path.join(saveroute, self.filename)
            for url in formats.m3u8Extract(self.url):
                filelist.append("file {}".format(os.path.join(newroute, file.getFileNameByUrl(url))).replace("\\","/"))
                downloader.download(url, newroute, file.getFileNameByUrl(url), headers=self.headers, **kwargs)
            file.writeToFile("\n".join(filelist),newroute,"filelist.txt")
            return
        downloader.download(self.url,saveroute,self.filename,headers = self.headers,**kwargs)