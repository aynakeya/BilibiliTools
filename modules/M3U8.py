from modules.base import BaseModule, registerModule
import os,subprocess

from sources.base import BaseSource, SourceSelector, CommonSource
from sources import *
from utils import formats
from utils.command import OptionParser

@registerModule
class M3U8(BaseModule):
    name = "M3U8"
    selector = SourceSelector(biliLive,
                              biliVideo,
                              biliBangumi,
                              biliAudio,
                              ImomoeSource,
                              KakadmSource)

    def getMethod(self):
        return {"m3u8": "combine m3u8 files to a single ts file",
                "m3u8-ffmpeg": "combine m3u8 files to a single ts file using ffmpeg"}

    def process(self, args):
        options = OptionParser(args)
        if options.command == "m3u8-ffmpeg":
            com_func = formats.m3u8FFmpegCombine
        else:
            com_func = formats.m3u8Combine
        for path in options.args:
            if os.path.exists(path):
                self.info("combineing %s" % path)
                com_func(path)
                self.info("success")
                continue
            downpath = os.path.join(Config.saveroute,path)
            if os.path.exists(downpath):
                self.info("combining %s" % downpath)
                com_func(downpath)
                self.info("success")
                continue
            self.info("not a valid path")

exports = [M3U8]