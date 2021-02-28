from apis import RegExpResponseContainer
from config import Config
from sources import MediaSource, CommonSource
from sources.video import VideoSource
from utils import file
import apis.kakadm as kakadmApi
import re, json

from utils.vhttp import httpGet


class KakadmSource(VideoSource):
    __source_name__ = "kakadm"

    base_url = "http://www.kakadm.com/"

    patternA = r"kakadm\.com\/anime\/[0-9]+"
    patternB = r"kakadm\.com\/anime\/[0-9]+\/[0-9]+"

    def __init__(self, aid, pid):
        self.aid = aid
        self.pid = pid
        self.pid_list = []
        self.title = ""
        self.src = ""
        self.episodes = {}

    @classmethod
    def initFromUrl(cls, url):
        if re.search(cls.patternB, url) != None:
            url = re.search(cls.patternB, url).group()
            url = url.replace("kakadm.com/anime/", "")
            ids = url.split("/")
            return cls(ids[0], ids[1])

        elif re.search(cls.patternA, url) != None:
            url = re.search(cls.patternA, url).group()
            url = url.replace("kakadm.com/anime/", "")
            return cls(url, "1")
        return cls("", "")

    @classmethod
    def applicable(cls, url):
        return re.search(cls.patternA, url) != None or re.search(cls.patternB, url) != None

    @property
    def info(self):
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Total Page": len(self.pid_list)
                }

    @property
    def video(self):
        return self.getVideo()

    def isValid(self):
        return self.src != ""

    def getBaseSources(self, all=False, **kwargs):
        if all:
            videos = []
            for pid in self.pid_list:
                kks = KakadmSource(self.aid, pid)
                kks.load()
                videos.append(kks.getVideo())
            return {"video": videos}
        else:
            return {"video": self.getVideo()}

    @CommonSource.wrapper.handleException
    def getVideo(self):
        src_container = RegExpResponseContainer(kakadmApi.getVideoUrl(self.aid, self.pid),
                                                src=(r"vid=(.*)\'",
                                                     lambda x: x[4:-1:]),
                                                )
        self.src = src_container.data["src"]
        container = RegExpResponseContainer(kakadmApi.resolveVideoUrl(self.src),
                                            real_url=(r"url:\"(.*)\"",
                                                      lambda x: x[5:-1:]),
                                            strip=" ",
                                            )
        real_url = container.data["real_url"]
        return MediaSource(container.data["real_url"],
                           Config.commonHeaders,
                           "{}.{}".format(self.title,
                                          file.getSuffixByUrl(real_url)))

    @CommonSource.wrapper.handleException
    def load(self, **kwargs):

        # raw_html = httpGet(self.player_url.format(aid=self.aid, pid=self.pid),
        #                    cookies=Config.getCookie("kakadm"))
        # html_text = raw_html.content.decode("utf-8").replace("\r", "").replace("\n", "")
        # self.title = re.search(r"play_title=\"((?!\";).)*\";", html_text).group()[12:-2:]
        container = RegExpResponseContainer(kakadmApi.getVideoInfo(self.aid, self.pid),
                                            strip=["\r", "\n"],
                                            title=(r"play_title=\"((?!\";).)*\";",
                                                   lambda x: x[12:-2:]),
                                            movurls=r"<div class=\"movurls\">((?!</div>).)*</div>")
        self.title = container.data["title"]
        self.pid_list = [str(i) for i in range(1, container.data["movurls"].count("</li>") + 1)]

        data_html = httpGet(self.src_api.format(aid=self.aid, pid=self.pid),
                            cookies=Config.getCookie("kakadm")).content.decode("utf-8")
        self.src = re.search(r"vid=(.*)\'", data_html).group()[4:-1:]
        # movulrs = re.search(r"<div class=\"movurls\">((?!</div>).)*</div>", html_text).group()
        # self.pid_list = [str(i) for i in range(1, movulrs.count("</li>") + 1)]

# a = KakadmSource.initFromUrl("http://www.kakadm.com/anime/2818/11/")
# a.load()
#
# print(a.getVideo().filename)
