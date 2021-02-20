from modules import BaseModule
from config import Config
from downloaders import downloaders, BaseDownloader
from sources import *
import getopt

from sources.base import SourceSelector, BaseSource
from utils.command import OptionParser


class Download(BaseModule):
    selector = SourceSelector(biliVideo,
                              biliAudio,
                              biliBangumi,
                              biliAudioList)

    def __init__(self):
        self.availableDl = {}


    def getMethod(self):
        return {"bdl": "Download bilibili video or audio (support video audio audiolist bangumi)."}

    def getOptions(self):
        return {
            "-{source name}": ["download the source by name",
                   "Available source name: ",
                   ["· video","· audio","· lyric","· cover","· damu"]],
            "-downloader=downloadername": ["use specific downloader.",
                            "Available downloaders:",
                            ["· aria2 - aria2",
                            "· requests - native requests downloader"]],
            "-option=value":["specify option for download",
                             ["video options:",
                              ["-page=page: specify which page",
                               "-qn=quality: specify which quality",
                               ["· %s - %s %s" % (
                                   x["quality"],
                                   x["desc"],
                                   "(SESSDATA Required)" if x["cookie"] else ""
                               ) for x in biliVideo.qualities],
                               "-all=1: download all page"
                               ],
                              "audio options:",
                              ["-qn=quality: specify which quality",
                               ["· 2 - 320k 高品质","· 1 - 196k 标准","· 0 - 128k 流畅"]
                               ],
                              ]
                             ]

        }

    def prepare(self):
        for dl in Config.useDownloader.keys():
            if downloaders.get(dl) is not None:
                self.availableDl[downloaders.get(dl).name] = downloaders.get(dl)()

    def process(self, args):
        options = OptionParser(args)

        kwargs = {}
        downloader = self.availableDl.get(Config.defaultDownloader)
        kwargs["qn"] = Config.defaultQuality
        target_source = []
        for key, value in options.options.items():
            if value == "":
                target_source.append(key)
                continue
            if key == "page" :
                kwargs["page"] = int(value)
            if key == "qn":
                kwargs["qn"] = int(value)
            if key == "all":
                kwargs["all"] = bool(int(value))
            if key == "downloader":
                downloader = self.availableDl.get(value)
        if downloader == None:
            self.info("Downloader didn't found")
            return
        for url in options.args:
            self.info("Start to download %s" % url)
            s = self.selector.select(url)
            s = s.initFromUrl(url) if s != None else None
            if s == None:
                self.info("%s not support" % url)
                continue
            if not s.downloadable:
                self.info("%s not support" % url)
                continue
            s.load(**kwargs)
            if s.isValid():
                self._download_source(downloader,target_source,s.getBaseSources(**kwargs))
                self.info("Download finish")
            else:
                self.info("this url may not be available now")

    def _download_source(self,downloader:BaseDownloader,target_source:list,sources:dict):
        for key,val in sources.items():
            if key in target_source:
                s: BaseSource
                if isinstance(val,list):
                    for s in val:
                        s.download(downloader,Config.saveroute)
                else:
                    s = val
                    s.download(downloader,Config.saveroute)

module = Download