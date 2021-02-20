from config import Config
from sources import MediaSource
from sources.video import VideoSource
from utils import file
import re,json

from utils.vhttp import httpGet


class KakadmSource(VideoSource):
    name = "kakadm"

    base_url = "http://www.kakadm.com/"
    player_url = "http://www.kakadm.com/anime/{aid}/{pid}/"
    src_api = "http://www.kakadm.com/e/action/player_i.php?id={aid}&pid={pid}"
    real_src_api = "http://www.kakadm.com/yun/yun.php?vid={src}"

    patternA = r"kakadm\.com\/anime\/[0-9]+"
    patternB = r"kakadm\.com\/anime\/[0-9]+\/[0-9]+"


    def __init__(self,aid,pid):
        self.aid = aid
        self.pid = pid
        self.title = ""
        self.src = ""
        self.episodes = {}

    @classmethod
    def initFromUrl(cls,url):
        if re.search(cls.patternB, url) != None:
            url = re.search(cls.patternB, url).group()
            url = url.replace("kakadm.com/anime/", "")
            ids = url.split("/")
            return cls(ids[0], ids[1])

        elif re.search(cls.patternA, url) != None:
            url = re.search(cls.patternA, url).group()
            url = url.replace("kakadm.com/anime/", "")
            return cls(url, "1")
        return cls("","")

    @classmethod
    def applicable(cls, url):
        return re.search(cls.patternA, url) != None or re.search(cls.patternB, url) != None

    @property
    def info(self):
        return [("Type", self.name),
                ("Title", self.title)
                ]

    @property
    def video(self):
        return self.getVideo()

    def isValid(self):
        return self.src != ""

    def getBaseSources(self,**kwargs):
        return {"video":self.getVideo()}

    def getVideo(self):
        try:
            player_html = httpGet(self.real_src_api.format(src=self.src),
                                  cookies=Config.getCookie("kakadm")).content.decode("utf-8")
            real_url = re.search(
                r"url:\"(.*)\"",player_html.replace(" ","")).group()[5:-1:]
            return MediaSource(real_url,Config.commonHeaders,
                               "{}.{}".format(self.title,
                                                 file.getSuffixByUrl(real_url)))
        except:
            return None

    def load(self,**kwargs):
        try:
            raw_html = httpGet(self.player_url.format(aid=self.aid,pid=self.pid),
                               cookies=Config.getCookie("kakadm"))
            html_text= raw_html.content.decode("utf-8")
            self.title = re.search(r"play_title=\"(.*)\";",html_text).group()[12:-2:]
            data_html = httpGet(self.src_api.format(aid=self.aid,pid=self.pid),
                                cookies=Config.getCookie("kakadm")).content.decode("utf-8")
            self.src = re.search(r"vid=(.*)\'",data_html).group()[4:-1:]
        except Exception as e:
            print(e)
            pass


# a = KakadmSource.initFromUrl("http://www.kakadm.com/anime/2818/11/")
# a.load()
#
# print(a.getVideo().filename)