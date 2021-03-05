from apis import JsonResponseContainer, RegExpResponseContainer
from sources.base import PictureSource, MediaSource, TextSource, CommonSource
from sources.bilibili import BilibiliSource
from utils.bilibili import videoIdConvertor
from config import Config
from apis.bilibili import video as videoApi
import re, json


class biliVideo(BilibiliSource):
    __source_name__ = "video"

    patternAv = r"av[0-9]+"
    patternBv = r"BV[0-9,A-Z,a-z]+"

    base_url = "https://www.bilibili.com/video/"

    qualities = [{'quality': 120, 'type': 'FLV', 'desc': '超清 4K',"cookie": True},
                 {'quality': 116, 'type': 'FLV', 'desc': '高清 1080P60', "cookie": True},
                 {'quality': 112, 'type': 'FLV', 'desc': '高清 1080P+', "cookie": True},
                 {'quality': 80, 'type': 'FLV', 'desc': '高清 1080P', "cookie": True},
                 {'quality': 74, 'type': 'FLV', 'desc': '高清 720P60', "cookie": True},
                 {'quality': 64, 'type': 'FLV', 'desc': '高清 720P', "cookie": True},
                 {'quality': 48, 'type': 'MP4', 'desc': '高清 720P (MP4)', "cookie": True},
                 {'quality': 32, 'type': 'FLV', 'desc': '清晰 480P', "cookie": False},
                 {'quality': 16, 'type': 'FLV', 'desc': '流畅 360P', "cookie": False}]

    def __init__(self, bid):
        self.bid = bid
        self.pages = []
        self.title = ""
        self.uploader = ""
        self.cover_url = ""
        self.currentPage = 1
        self.status = 200

    @classmethod
    def initFromId(cls, id):
        bid = ""
        if "BV" in id:
            bid = id
        if "av" in id:
            bid = videoIdConvertor.av2bv(id)
        return cls(bid)

    @classmethod
    def initFromUrl(cls, url):
        v = cls("")
        if re.search(cls.patternBv, url):
            v.bid = re.search(cls.patternBv, url).group()
        if re.search(cls.patternAv, url):
            v.bid = videoIdConvertor.av2bv(re.search(cls.patternAv, url).group()[2::])
        if re.search(r"p=[0-9]+", url):
            v.currentPage = int(re.search(r"p=[0-9]+", url).group()[2::])
        return v

    @classmethod
    def initFromData(cls, id, title, uploader, cover_url, pages):
        v = cls.initFromId(id)
        v.title = title
        v.uploader = uploader
        v.cover_url = cover_url
        v.pages = pages
        return v

    @property
    def id(self):
        return self.bid

    @property
    def video(self):
        return self.getVideo()

    @CommonSource.wrapper.handleException
    def getVideo(self, page=0, qn=116):
        if page == 0:
            page = self.currentPage
        urls = self._getPlayurl(page, qn)
        if len(urls) == 0:
            return None
        url = urls[0]
        suffix = url.split("?")[0].split(".")[-1]
        return MediaSource(url,
                           {"origin": "www.bilibili.com", "referer": self.base_url + self.bid,
                                         "user-agent": Config.commonHeaders["user-agent"]}
                           ,
                           self._parseTitle("video", page, suffix))

    @property
    def cover(self):
        if self.cover_url != "":
            suffix = self.cover_url.split("?")[0].split(".")[-1]
            return PictureSource(self.cover_url, {}, ".".join([self.title, suffix]), "")

    @property
    def danmu(self):
        return self.getDanmu()

    def getDanmu(self, page=0):
        if page == 0:
            page = self.currentPage
        return TextSource(videoApi.API.danmu_api(self._getPageCid(page)),
                          Config.commonHeaders,
                          self._parseTitle("danmu", page, "xml"),
                          "")

    @property
    def info(self):
        qs = ["%s: %s(%s)" % (key, value[1], value[0])for key, value in self._getQualities().items()]
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Bid": self.bid,
                "Cid": str(self._getPageCid(self.currentPage)),
                "Uploader": self.uploader,
                "Current Page": self._getPageName(self.currentPage),
                "Available Qualities": qs,
                "Total page": str(len(self.pages)),
                "Page List":["P%s - %s" % (x["page"], x["pagename"]) for x in self.pages]
                }

    @classmethod
    def applicable(cls, url):
        return re.search(cls.patternAv, url) != None or re.search(cls.patternBv, url) != None

    def _getPages(self):
        container = JsonResponseContainer(videoApi.getVideoCid(self.bid),
                                          data="data")
        self.pages = [{"page": d["page"], "pagename": d["part"], "cid": d["cid"]} for d in container.data["data"]]

    @CommonSource.wrapper.handleException
    def load(self, **kwargs):
        container = JsonResponseContainer(videoApi.getVideoInfo(self.bid),
                                          title = "data.View.title",
                                          uploader = "data.View.owner.name",
                                          cover = "data.View.pic")
        self.title = container.data["title"]
        self.uploader = container.data["uploader"]
        self.cover_url = container.data["cover"]
        self._getPages()

    def _getPageCid(self, page):
        cid = 0
        for p in self.pages:
            if p["page"] == page:
                cid = p["cid"]
                break
        return cid

    def _getPageName(self, page):
        pn = ""
        for p in self.pages:
            if p["page"] == page:
                pn = p["pagename"]
                break
        return pn

    def _getQualities(self, page=1):
        quality = {}
        cid = self._getPageCid(page)
        if cid == 0:
            return quality
        container = JsonResponseContainer(videoApi.getPlayUrl(self.bid, cid, quality=32),
                                          formats=("data.accept_format",
                                                   lambda x:x.split(",")),
                                          quality = "data.accept_quality",
                                          desc = "data.accept_description")
        for index, qn in enumerate(container.data["quality"]):
            quality[qn] = (container.data["formats"][index], container.data["desc"][index])
        return quality

    def getBaseSources(self, page=0, qn=116,all=False,**kwargs):
        if not self.isValid(): return {}
        if all:
            return {"video": [self.getVideo(page=p,qn=qn)
                               for p in range(1,len(self.pages)+1)],
                "danmu": self.getDanmu(page=page),
                "cover": self.cover}
        return {"video": self.getVideo(page=page,qn=qn),
                "danmu": self.getDanmu(page=page),
                "cover": self.cover}

    def _getPlayurl(self, page, qn):
        urls = []
        cid = self._getPageCid(page)
        if cid == 0:
            return []
        container = JsonResponseContainer(videoApi.getPlayUrl(self.bid,cid,quality=qn),
                                          durl = "data.durl")
        for u in container.data["durl"]:
            urls.append(u["url"])
            if u["backup_url"] != None:
                urls.append(u["backup_url"])
        return urls


    def _parseTitle(self, type, page, suffix):
        if (type == "video"):
            if (len(self.pages) > 1):
                return ".".join(
                    ["%s (P%s %s) - %s" % (self.title, page, self._getPageName(page), self.uploader), suffix])
            else:
                return ".".join([self.title + " - " + self.uploader, suffix])
        if (type == "cover"):
            return ".".join([self.title, suffix])
        if (type == "danmu"):
            if (len(self.pages) > 1):
                return ".".join(["%s (P%s %s) - %s" % (self.title, page, self._getPageName(page), self.uploader), "xml"])
            else:
                return ".".join([self.title + " - " + self.uploader, "xml"])

    def isValid(self):
        if self.status == 404: return False
        return True if len(self.pages) > 0 else False


class biliBangumi(biliVideo):
    __source_name__ = "bangumi"

    patterns = [r"ep[0-9]+",
                r"ss[0-9]+"]

    def __init__(self, ep_id):
        super(biliBangumi, self).__init__("")
        self.ep_id = ep_id

    @property
    def info(self):
        qs = ["%s : %s(%s)" % (key, value[1], value[0]) for key, value in self._getQualities().items()]
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Bid": self.bid,
                "Cid": str(self._getPageCid(self.currentPage)),
                "Current Episode": self._getPageName(self.currentPage),
                "Available Qualities": qs,
                "Total page": str(len(self.pages)),
                "Page List":[x["pagename"] for x in self.pages]
                }

    @classmethod
    def applicable(cls, url):
        ap = False
        for p in cls.patterns:
            ap = ap or re.search(p, url) != None
        return ap

    @classmethod
    def initFromUrl(cls, url):
        if cls.applicable(url):
            for p in cls.patterns:
                if re.search(p,url) != None:
                    return biliBangumi(re.search(p,url).group())
        return biliBangumi("")


    def _getQualities(self, page=1):

        quality = {}
        cid = self._getPageCid(page)
        if cid == 0:
            return quality
        container = JsonResponseContainer(videoApi.getBangumiPlayUrl(self.bid, cid, quality=32),
                                          formats=("data.accept_format",
                                                   lambda x: x.split(",")),
                                          quality="data.accept_quality",
                                          desc="data.accept_description")
        for index, qn in enumerate(container.data["quality"]):
            quality[qn] = (container.data["formats"][index], container.data["desc"][index])
        return quality

    def _getPlayurl(self, page, qn):

        urls = []
        cid = self._getPageCid(page)
        if cid == 0:
            return []
        container = JsonResponseContainer(videoApi.getBangumiPlayUrl(self.bid, cid, quality=qn),
                                          durl="result.durl")
        for u in container.data["durl"]:
            urls.append(u["url"])
            if u["backup_url"] != None:
                urls.append(u["backup_url"])
        return urls

    @CommonSource.wrapper.handleException
    def load(self, **kwargs):
        if self.ep_id == "":
            return
        container = RegExpResponseContainer(videoApi.getBangumiInfo(self.ep_id),
                                            state = (r"__INITIAL_STATE__={(.*?)]};",
                                                     lambda x:x[18:-1:]))
        initial_state = json.loads(container.data["state"])
        self.title = initial_state["mediaInfo"]["title"]
        self.cover_url = "https:" + initial_state["mediaInfo"]["cover"]
        eplist = initial_state["epList"]
        self.bid = eplist[0]["bvid"]
        self.currentPage = 1
        pages = []
        epid = ""
        if "ep" in self.ep_id:
            epid = str(re.search(r"ep[0-9]+", self.ep_id).group()[2:])
        for index, ep in enumerate(eplist, start=1):
            pages.append(
                {"page": index, "pagename": "%s %s" % (ep["titleFormat"], ep["longTitle"]), "cid": ep["cid"]})
            if epid == str(ep["id"]):
                self.currentPage = index
        self.pages = pages

    def _parseTitle(self, type, page, suffix):
        if (type == "video"):
            return ".".join(["%s: %s" % (self.title, self._getPageName(page)), suffix])
        if (type == "cover"):
            return ".".join([self.title, suffix])
        if (type == "danmu"):
            return ".".join(["%s: %s" % (self.title, self._getPageName(page)), suffix])


# class biliVideoList():
#     name = "videolist"
#
#     pattern = r"fid=[0-9]+"
#
#     # favApi = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
#     favApi = "https://api.bilibili.com/x/v3/fav/resource/list?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
#     # addApi = "https://api.bilibili.com/medialist/gateway/coll/resource/deal"
#     addApi = "https://api.bilibili.com/x/v3/fav/resource/deal"
#
#     downloadable = True
#     watchable = False
#
#     def __init__(self, media_id):
#         self.media_id = media_id
#         self.videos = []
#
#     @property
#     def id(self):
#         return self.media_id
#
#     @classmethod
#     def applicable(cls, url):
#         return re.search(cls.pattern, url) != None
#
#     @classmethod
#     def initFromUrl(cls, url):
#         pattern = r"fid=[0-9]+"
#         return cls(re.search(pattern, url).group()[4::]) if re.search(pattern, url) != None else cls("")
#
#     def getInfo(self, maxNum=1000, **kwargs):
#         self.clearData()
#         pn = 1
#         num = 0
#         while True:
#             data = httpGet(self.favApi % (self.media_id, pn), cookies=Config.commonCookies,
#                            headers=Config.commonHeaders)
#             if data == None: return
#             data = data.json()
#             if data["data"]["info"]["media_count"] == 0:
#                 break
#             for media in data["data"]["medias"]:
#                 if num >= maxNum:
#                     return
#                 bid = media["bvid"]
#                 title = media["title"]
#                 cover = media["cover"]
#                 uploader = media["upper"]["name"]
#                 # pages = [{"page": p["page"], "pagename": p["title"], "cid": p["id"]} for p in media["pages"]]
#                 v = biliVideo.initFromData(bid, title, uploader, cover, [])
#                 if media["attr"] == 0:
#                     v._getPages()
#                 else:
#                     v.status = 404
#                 self.videos.append(v)
#                 num += 1
#             pn += 1
#
#     def clearData(self):
#         self.videos.clear()
#
#     def download(self, downloader=None, **kwargs):
#         if not self.isValid(): return
#         if downloader == None:
#             return
#         video: biliVideo
#         for video in self.videos:
#             video.download(downloader=downloader, **kwargs)
#
#     def dumpInfo(self):
#         return [("Type", self.name),
#                 ("Media_id", self.media_id),
#                 ("Videoo number", len(self.videos))
#                 ]
#
#     def isValid(self):
#         return True if len(self.videos) > 0 else False
#
#     def addVideo(self, aid):
#         data = httpPost(self.addApi,
#                         headers={"origin": "https://www.bilibili.com", "referer": "https://www.bilibili.com"},
#                         cookies=Config.commonCookies,
#                         data={'rid': int(aid), 'type': 2, 'add_media_ids': int(self.media_id), 'del_media_ids': "",
#                               'jsonp': 'jsonp'})
#         return data.json() if data != None else None
