from downloaders import downloaders, BaseDownloader
from sources import *
from modules.base import RunningMode, BaseModule, registerModule
from config import Config
from sources.base.interface import DownloadableSource
from utils.bilibili import QrLogin

from sources.base import SourceSelector
from utils.command import OptionParser

@registerModule
class Download(BaseModule):
    name = "Bilibili.Download"
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
                   ["· video","· audio","· lyric","· cover","· danmu"]],
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
            s.load(**kwargs)
            if s.isValid():
                self._download_source(downloader,target_source,s.getBaseSources(**kwargs))
                self.info("Download finish")
            else:
                self.info("this url may not be available now")

    def _download_source(self,downloader:BaseDownloader,target_source:list,sources:dict):
        for key,val in sources.items():
            if key in target_source:
                if key == "danmu":
                    d = self.availableDl.get("requests")
                else:
                    d = downloader
                if isinstance(val,list):
                    for s in val:
                        if isinstance(s,DownloadableSource):
                            s.download(d,Config.saveroute)
                else:
                    if isinstance(val, DownloadableSource):
                        val.download(d,Config.saveroute)

@registerModule
class Login(BaseModule):
    name = "Bilibili.Login"

    def getMethod(self):
        return {"qrlogin":"get cookie using qrcode login"}

    def require(self):
        if self.running_mode == RunningMode.CONSOLE:
            if not QrLogin.isLogin():
                if input(
                        "We found that there is no sessdata included, would you like to login using qrcode y/n ?") == "y":
                    QrLogin.manuallylogin()


    def process(self, args):
        if self.running_mode == "console":
            QrLogin.manuallylogin()
        else:
            ql = QrLogin()
            self.info("getting qrcode")
            ql.getQrcode()
            self.info("Please scan qrcode using your application")
            if ql.getResult():
                self.info("login success, you Sessdata is %s" % ql.getSessdata())
                Config.getCookie("bilibili")["SESSDATA"] = ql.getSessdata()
                Config.saveCookie()
            else:
                self.info("fail, please try again")

@registerModule
class VideoIdConverter(BaseModule):
    name = "Bilibili.VideoIdConverter"

    videoUrl = "https://www.bilibili.com/video/%s"
    patternAv = r"av[0-9]+"
    patternBv = r"BV[0-9,A-Z,a-z]+"
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = dict(("fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"[i], i) for i in range(58))
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608

    @classmethod
    def bv2av(cls, x):
        r = 0
        for i in range(6):
            r += cls.tr[x[cls.s[i]]] * 58 ** i
        return (r - cls.add) ^ cls.xor

    @classmethod
    def av2bv(cls, x):
        x = (int(x) ^ cls.xor) + cls.add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[cls.s[i]] = cls.table[x // 58 ** i % 58]
        return ''.join(r)

    @classmethod
    def urlConvert(cls, url):
        if re.search(cls.patternBv, url):
            return cls.videoUrl % ("av%s" % cls.bv2av(re.search(cls.patternBv, url).group()))
        if re.search(cls.patternAv, url):
            return cls.videoUrl % cls.av2bv(int(re.search(cls.patternAv, url).group()[2::]))
        return ""

    def getMethod(self):
        return {"bidconvert":"convert between bv and av"}


    def process(self, args):
        for url in OptionParser(args).args:
            urla = self.urlConvert(url)
            if urla == "":
                self.info("%s is not a proper video id" % url)
                continue
            self.info("%s -> %s" % (url, urla))

exports = [Download,Login,VideoIdConverter]
