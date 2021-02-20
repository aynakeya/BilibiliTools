from downloaders import BaseDownloader
from sources.base import BaseSource
from utils import formats,file
import os

class MediaSource(BaseSource):
    name = "media"

    downloadable = True
    watchable = True

    def __init__(self,url,headers,filename):
        self.url = url
        self.headers = headers
        self.filename = filename

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