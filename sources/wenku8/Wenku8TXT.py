import json

from config import Config
from downloaders import requestsDownloader
from sources import TextSource
from sources.wenku8 import Wenku8Source
import re

from utils.http import httpGet


class Wenku8TXT(Wenku8Source):
    name = "txt"

    baseUrl = "https://www.wenku8.net/book/{id}.htm"

    download_api = "http://dl.wenku8.com/down.php?type=utf8&id={id}"

    pattern = r"[0-9]+\.htm"

    def __init__(self,id):
        self.bid = id
        self.title= ""
        self.author = ""
        self.publisher = ""

    @property
    def id(self):
        return id

    @property
    def info(self):
        return [("Type", self.getSourceName()),
                ("Title", self.title),
                ("Author", self.author),
                ("Publisher", self.publisher)]

    @property
    def txt(self):
        return TextSource(self.download_api.format(id=self.bid),
                          Config.commonHeaders,
                          self.getParsedTitle()+".txt","")

    @classmethod
    def initFromUrl(cls,url):
        return cls(re.search(cls.pattern, url).group()[:-4:]) \
            if re.search(cls.pattern, url) !=None else cls("")
    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    def getBaseSources(self):
        return {"text":self.txt}

    def load(self):
        if self.bid == "": return
        rawhtml = httpGet(self.baseUrl.format(id = self.bid),
                          headers = Config.commonHeaders)
        if rawhtml == None:return
        try:
            rawhtml = rawhtml.content.decode("gbk")
            title = re.search(r"<title>(.*)</title>", rawhtml).group()[7:-7:].split(" - ")
            self.title = title[0]
            self.publisher =title[2]
            self.author = title[1]
        except Exception as e:
            print(repr(e))
            pass

    def getParsedTitle(self):
        return "{} - {}".format(self.title,self.author)

    def isValid(self):
        return self.title != ""
