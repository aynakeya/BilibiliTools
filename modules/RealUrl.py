from modules.base import BaseModule, registerModule
from sources import *

from sources.base import SourceSelector, BaseSource
from utils.command import OptionParser

@registerModule
class RealUrl(BaseModule):
    name = "RealUrl"
    selector = SourceSelector(Wenku8TXT,
                              KakadmSource,
                              ImomoeSource,
                              biliLive)

    def __init__(self):
        pass


    def getMethod(self):
        return {"realurl": "get real resource url."}

    def getOptions(self):
        return {
            "-{source name}": ["download the source by name",
                   "Available source name: ",
                   ["· text","· video"]],
        }

    def process(self, args):
        options = OptionParser(args)

        kwargs = {}
        target_source = []
        for key, value in options.options.items():
            if value == "":
                target_source.append(key)
                continue
        for url in options.args:
            self.info("Getting Real Url %s" % url)
            s = self.selector.select(url)
            s = s.initFromUrl(url) if s != None else None
            if s == None:
                self.info("%s not support" % url)
                continue
            s.load(**kwargs)
            if s.isValid():
                self._printRealUrl(target_source,s.getBaseSources(**kwargs))
            else:
                self.info("this url may not be available now")

    def _printRealUrl(self,target_source:list,sources:dict):
        for key,val in sources.items():
            if key in target_source:
                s: BaseSource
                if isinstance(val,list):
                    for s in val:
                        self.info("{}: {}".format(key,s.url))
                else:
                    s = val
                    self.info("{}: {}".format(key,s.url))

exports = [RealUrl]