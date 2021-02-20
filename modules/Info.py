from modules import BaseModule
from sources.base import SourceSelector
from sources import *


class Info(BaseModule):
    name = "Info"
    selector = SourceSelector(biliLive,
                              biliVideo,
                              biliAudioList,
                              biliAudio,
                              biliBangumi,
                              Wenku8TXT,
                              ImomoeSource,
                              KakadmSource)

    def getMethod(self):
        return {"info": "Print out basic information."}

    def process(self, args):
        for url in [s for s in args.split(" ")[1:] if s != ""]:
            self.info("Start to get information of %s" % url)
            s =  self.selector.select(url)
            s =s.initFromUrl(url) if s != None else None
            if s == None:
                self.info("Url %s not support" % url)
                continue
            s.load()
            if s.isValid():
                self.info("--")
                for key, value in s.info:
                    print("%s: %s" % (key,value))
                self.info("--")
            else:
                self.info("Url %s may not be available now" % url)

exports = [Info]