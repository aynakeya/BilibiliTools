from modules import BaseModule, RunningMode
import subprocess

from sources.base import BaseSource, SourceSelector
from sources import *
from sources.base.interface import WatchableSource
from utils.command import OptionParser

from gui.MPVGUI import MPVGUI

class MPV(BaseModule):
    name = "MPV"
    selector = SourceSelector(biliLive,
                              biliVideo,
                              biliBangumi,
                              biliAudio,
                              ImomoeSource,
                              KakadmSource)

    def getMethod(self):
        return {"mpv": "Play by mpv"}

    def getOptions(self):
        return {"-gui=1":["GUI only option",
                          "play in the embedded mpv gui"]}

    def mpvHeaderString(self,headers:dict):
        return "--http-header-fields=%s" % \
                  ",".join("\"%s:%s\"" %(x,y) for x,y in headers.items())

    def getPlayableSource(self,sources:dict) -> BaseSource:
        for val in sources.values():
            val:BaseSource
            if isinstance(val,WatchableSource) and isinstance(val,BaseSource):
                return val
        return None


    def playByMPV(self,bs:BaseSource):
        if bs == None:
            self.info("无法获取到可播放链接")
        title = bs.filename
        if len(bs.filename.split(".")) >1:
            title = ".".join(bs.filename.split(".")[:-1:])
        self.info("starting mpv")
        subprocess.Popen("mpv --force-media-title=\"%s\" %s \"%s\"" %(title,
                                                                      self.mpvHeaderString(bs.headers),
                                                                      bs.url))

    def playByEmbeddedMPV(self,bs: BaseSource):
        if self.running_mode != RunningMode.GUI:
            return
        if bs == None:
            self.info("无法获取到可播放链接")
        title = bs.filename
        if len(bs.filename.split(".")) > 1:
            title = ".".join(bs.filename.split(".")[:-1:])
        self.info("playing {}".format(title))
        mpvgui:MPVGUI = MPVGUI.getInstance()
        mpvgui.play(bs.url,headers=bs.headers)

    def process(self, args):
        ops = OptionParser(args)
        if (len(ops.args) < 1):
            self.info("no url provided")
            return
        url = ops.args[0]
        s = self.selector.select(url)
        s = s.initFromUrl(url) if s != None else None
        if s == None:
            self.info("%s not support" % url)
            return
        s.load()
        if s.isValid():
            if (ops.getOption("gui") != None):
                self.playByEmbeddedMPV(self.getPlayableSource(s.getBaseSources()))
            else:
                self.playByMPV(self.getPlayableSource(s.getBaseSources(**(ops.getParsedOptions()))))
        else:
            self.info("this url may not be available now")


exports = [MPV]