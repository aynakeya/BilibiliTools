from modules import BaseModule
from config import Config
from downloaders import downloaders
from models import models,modelSelector
import getopt


class Download(BaseModule):
    def __init__(self):
        self.availableDl = {}


    def getMethod(self):
        return {"download": "Download video or audio.",
                "dl": "Download video or audio."}

    def getOptions(self):
        return {
            "-l/--lyric": "download lyric (If have)",
            "-c/--cover": "download cover (If have)",
            "-d/--danmu": "download damu (If have)",
            "-a/--all": "download all page (if have) in the video",
            "-p/--page": "download specfic page of the video",
            "-m/--maxnumber": "set the max number of audio or video in a playlist you want to download",
            "--ignore": "ignore download anything that is not chosen by user. eg. \"-c --ignore\" will only download cover and skip video file or audio file",
            "--downloader": "use specific downloader.\n" +
                            "Available downloaders:\n" +
                            "· aria2 - aria2\n· requests - native requests downloader",
            "-q/--quality": "choose the quality.\n" +
                            "Available Audio Quality:\n" +
                            "· 2 - 320k 高品质\n· 1 - 196k 标准\n· 0 - 128k 流畅\n" +
                            "Available Video Quality:\n" +
                            "\n".join(["· %s - %s %s" % (
                                x["quality"],
                                x["desc"],
                                "(SESSDATA Required)" if x["cookie"] else ""
                            ) for x in models["video"].qualities]
                                      )
        }

    def prepare(self):
        for dl in Config.useDownloader.keys():
            if downloaders.get(dl) is not None:
                self.availableDl[downloaders.get(dl).name] = downloaders.get(dl)()

    def process(self, args):
        try:
            options, args = getopt.getopt(args.split(" ")[1:], "lcdaq:m:p:",
                                          ["lyric", "cover", "danmu", "all", "ignore",
                                           "downloader=", "quality=", "maxnumber=", "page="
                                           ])
        except:
            self.info("illegal option")
            return

        kwargs = {}
        # todo default config
        kwargs["qn"] = Config.defaultQuality
        kwargs["downloader"] = self.availableDl.get(Config.defaultDownloader)
        for key, value in options:
            if key == "-l" or key == "--lyric":
                kwargs["lyric"] = True
            if key == "-c" or key == "--cover":
                kwargs["cover"] = True
            if key == "-d" or key == "--damu":
                kwargs["damu"] = True
            if key == "-a" or key == "--all":
                kwargs["all"] = True
            if key == "-p" or key == "--page":
                kwargs["page"] = int(value)
            if key == "-q" or key == "--quality":
                kwargs["qn"] = int(value)
            if key == "-m" or key == "--maxnumber":
               kwargs["maxNum"] = int(value)
            if key == "--downloader":
                kwargs["downloader"] = self.availableDl.get(value)
            if key == "--ignore":
                kwargs["audio"] = False
                kwargs["video"] = False
        if kwargs["downloader"] == None:
            self.info("Downloader didn't found")
            return
        for url in [s for s in args if s != ""]:
            self.info("Start to download %s" % url)
            m = modelSelector(url).initFromUrl(url) if modelSelector(url) != None else None
            if m == None:
                self.info("%s not support" %url)
                continue
            if not m.downloadable:
                self.info("%s not support" % url)
                continue
            m.getInfo(**kwargs)
            if m.isValid():
                m.download(**kwargs)
                self.info("Download finish")
            else:
                self.info("this url may not be available now")

module = Download