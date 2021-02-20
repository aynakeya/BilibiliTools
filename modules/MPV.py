from modules import BaseModule
import subprocess

from sources.base import BaseSource, SourceSelector, CommonSource
from sources import *


class MPV(BaseModule):
    selector = SourceSelector(biliLive,
                              biliVideo,
                              biliBangumi,
                              biliAudio,
                              biliAudioList)
    playable = ["video","audio"]

    def getMethod(self):
        return {"mpv": "Play by mpv"}

    def mpvHeaderString(self,headers:dict):
        return "--http-header-fields=%s" % \
                  ",".join("\"%s:%s\"" %(x,y) for x,y in headers.items())

    def getPlayableSource(self,sources:dict):
        for s in self.playable:
            for key,val in sources.items():
                if key == s:
                    return val
        return None

    def playByMPV(self,source:CommonSource):
        bs = self.getPlayableSource(source.getBaseSources())
        bs:BaseSource
        if bs == None:
            self.info("无法获取到可播放链接")
        title = bs.filename
        if len(bs.filename.split(".")) >1:
            title = ".".join(bs.filename.split(".")[:-1:])
        subprocess.Popen("mpv --force-media-title=\"%s\" %s \"%s\"" %(title,
                                                                      self.mpvHeaderString(bs.headers),
                                                                      bs.url))

    def process(self, args):
        args = args.split(" ")[1:]
        if (len(args) < 1):
            self.info("no url provided")
            return
        url = args[0]
        s = self.selector.select(url)
        s = s.initFromUrl(url) if s != None else None
        if s == None:
            self.info("%s not support" % url)
            return
        if not s.watchable:
            self.info("%s not support" % url)
            return
        s.load()
        if s.isValid():
            self.info("starting mpv")
            self.playByMPV(s)
        else:
            self.info("this url may not be available now")


module = MPV