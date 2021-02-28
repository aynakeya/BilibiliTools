from apis import JsonResponseContainer, RegExpResponseContainer
from sources.base import MediaSource, CommonSource
from utils.vhttp import httpGet
from config import Config
from sources.bilibili import BilibiliSource
from apis.bilibili import live as liveApi
import re


class biliLive(BilibiliSource):
    __source_name__ = "live"

    patternUrl = r"live\.bilibili\.com\/[0-9]+"
    patternId = r"live[0-9]+"

    baseUrl = "https://live.bilibili.com/%s"

    # from https://github.com/wbt5/real-url/blob/master/bilibili.py
    def __init__(self, rid):
        self.rid = rid
        self.room_id = ""
        self.title = "Bilibili Live %s" % rid

    @property
    def id(self):
        return self.rid

    @property
    def video(self):
        return self.getVideo()

    @CommonSource.wrapper.handleException
    def getVideo(self, format="hls"):
        container = JsonResponseContainer(liveApi.getRealUrlByFormat(self.room_id,
                                                                     format),
                                          durl="data.durl")
        return MediaSource(container.data["durl"][-1]['url'],
                           {"origin": "www.bilibili.com", "referer": self.baseUrl % self.id,
                            "user-agent": Config.commonHeaders["user-agent"]},
                           self.title)

    @property
    def info(self):
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Room ID": self.rid,
                "Real Room ID": self.room_id,
                "Available Formats": "hls,flv"}

    @classmethod
    def applicable(cls, url):
        return bool(re.search(cls.patternUrl, url)) or bool(re.search(cls.patternId, url))

    def isValid(self):
        return self.room_id != ""

    @CommonSource.wrapper.handleException
    def load(self,**kwargs):
        container = JsonResponseContainer(liveApi.getLiveInfo(self.rid),
                                          live_stauts="data.live_status",
                                          room_id="data.room_id")
        if container.data["live_stauts"] == 1:
            self.room_id = container.data["room_id"]
        res = httpGet(self.baseUrl % self.rid,
                      headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.id,
                               "user-agent": Config.commonHeaders["user-agent"]}
                      ).content.decode("utf-8")
        tp = r"<title id=\"link-app-title\">.*<\/title>"
        if re.search(tp, res):
            self.title = re.search(tp, res).group()[27:-8:]

    @classmethod
    def initFromUrl(cls, url):
        if re.search(cls.patternUrl, url):
            return cls(re.search(cls.patternUrl, url).group()[18::])
        if re.search(cls.patternId, url):
            return cls(re.search(cls.patternId, url).group()[4::])
        return cls("")

    def getBaseSources(self, format="hls",**kwargs):
        if self.isValid():
            return {"video": self.getVideo(format=format)}
        return {}
