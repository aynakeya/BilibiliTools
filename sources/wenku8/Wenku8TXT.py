from apis import RegExpResponseContainer
import apis.wenku8 as wenku8api
from config import Config
from sources import TextSource, CommonSource
from sources.wenku8 import Wenku8Source
import re


class Wenku8TXT(Wenku8Source):
    __source_name__ = "txt"

    baseUrl = "https://www.wenku8.net/book/{id}.htm"

    download_api = "http://dl.wenku8.com/down.php?type=utf8&id={id}"

    pattern = r"www\.wenku8\.net/book/[0-9]+\.htm"

    def __init__(self,id):
        self.bid = id
        self.title= ""
        self.author = ""
        self.publisher = ""

    @property
    def id(self):
        return self.bid

    @property
    def info(self):
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Book ID": self.bid,
                "Author": self.author,
                "Publisher": self.publisher}
    @property
    def txt(self):
        return TextSource(self.download_api.format(id=wenku8api.getFileUrl(self.bid)),
                          Config.commonHeaders,
                          self.getParsedTitle()+".txt","")

    @classmethod
    def initFromUrl(cls,url):
        rs = re.search(cls.pattern, url)
        if rs == None: cls("")
        rs = rs.group().replace(".htm","")\
            .replace("www.wenku8.net/book/","")
        return cls(rs)

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    def getBaseSources(self):
        return {"text":self.txt}

    @CommonSource.wrapper.handleException
    def load(self):
        if self.bid == "": return
        container = RegExpResponseContainer(wenku8api.getBookInfo(self.bid),
                                            info=(r"<title>(.*)</title>",
                                                  lambda x: x[7:-8:]))
        title = container.data["info"].split(" - ")
        self.publisher = title[2]
        self.author = title[1]
        self.title = title[0]

    def getParsedTitle(self):
        return "{} - {}".format(self.title,self.author)

    def isValid(self):
        return self.title != ""
