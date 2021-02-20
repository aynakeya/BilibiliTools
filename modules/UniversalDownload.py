from modules import BaseModule
from config import Config
from downloaders import downloaders, BaseDownloader
from sources import *
import getopt

from sources.base import SourceSelector, BaseSource
from utils.command import OptionParser


class UniversalDownload(BaseModule):
    name = "UniversalDownload"
    selector = SourceSelector(Wenku8TXT,
                              KakadmSource,
                              ImomoeSource)

    def __init__(self):
        self.availableDl = {}


    def getMethod(self):
        return {"download": "universal download command."}

    def getOptions(self):
        return {
            "-{source name}": ["download the source by name",
                   "Available source name: ",
                   ["· text","· video"]],
            "-downloader=downloadername": ["use specific downloader.",
                            "Available downloaders:",
                            ["· aria2 - aria2",
                            "· requests - native requests downloader"]]
        }

    def prepare(self):
        for dl in Config.useDownloader.keys():
            if downloaders.get(dl) is not None:
                self.availableDl[downloaders.get(dl).name] = downloaders.get(dl)()

    def process(self, args):
        options = OptionParser(args)

        kwargs = {}
        downloader = self.availableDl.get(Config.defaultDownloader)
        target_source = []
        for key, value in options.options.items():
            if value == "":
                target_source.append(key)
                continue
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
                        self.info("Downloading {}".format(s.filename))
                        s.download(downloader,Config.saveroute)
                else:
                    s = val
                    self.info("Downloading {}".format(s.filename))
                    s.download(downloader,Config.saveroute)

exports = [UniversalDownload]