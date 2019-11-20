from pyaria2 import Aria2RPC
from config import Config
from utils import filenameparser

class ariaDownloader():
    name = "aria2"
    def __init__(self, url=Config.aria2rpc, token=Config.aria2token):
        self.rpc = Aria2RPC(url=url, token=token)

    def parseHeader(self,headers):
        return ["%s:%s" % h for h in headers.items()]

    def download(self, url, route, filename, **kwargs):
        kwargs["dir"] = route
        kwargs["out"] = filenameparser(filename)
        if "headers" in kwargs.keys():
            kwargs["header"] = self.parseHeader(kwargs.pop("headers"))
        self.rpc.addUri([url], kwargs)

