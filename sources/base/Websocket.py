from downloaders import BaseDownloader
from sources.base import BaseSource
from sources.base.interface import DownloadableSource, WatchableSource
from utils import formats,file
import os

class MediaSource(BaseSource):
    __source_name__ = "websocket"

    def __init__(self,url,headers,filename,register_data):
        self.url = url
        self.headers = headers
        self.filename = filename
        self.register_data = register_data