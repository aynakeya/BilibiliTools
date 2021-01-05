from utils import httpGet, httpPost, videoIdConvertor
from config import Config
from downloaders import downloaders
import re, json


class biliVideo():
    name = "video"

    patternAv = r"av[0-9]+"
    patternBv = r"BV[0-9,A-Z,a-z]+"

    downloadable = True
    watchable = True

    '''{'quality': 120, 'type': 'FLV', 'desc': '超清 4K'},'''
    qualities = [{'quality': 120, 'type': 'FLV', 'desc': '超清 4K',"cookie": True},
                 {'quality': 116, 'type': 'FLV', 'desc': '高清 1080P60', "cookie": True},
                 {'quality': 112, 'type': 'FLV', 'desc': '高清 1080P+', "cookie": True},
                 {'quality': 80, 'type': 'FLV', 'desc': '高清 1080P', "cookie": True},
                 {'quality': 74, 'type': 'FLV', 'desc': '高清 720P60', "cookie": True},
                 {'quality': 64, 'type': 'FLV', 'desc': '高清 720P', "cookie": True},
                 {'quality': 48, 'type': 'MP4', 'desc': '高清 720P (MP4)', "cookie": True},
                 {'quality': 32, 'type': 'FLV', 'desc': '清晰 480P', "cookie": False},
                 {'quality': 16, 'type': 'FLV', 'desc': '流畅 360P', "cookie": False}]

    # videoUrl = "https://www.bilibili.com/video/av%s"
    baseUrl = "https://www.bilibili.com/video/%s"
    # pagesApi = "https://www.bilibili.com/widget/getPageList?aid=%s"
    pagesApi = "https://api.bilibili.com/x/player/pagelist?bvid=%s"
    detailApi = "https://api.bilibili.com/x/web-interface/view/detail?bvid=%s&aid=&jsonp=jsonp"
    playurlApi = "https://api.bilibili.com/x/player/playurl?avid=&bvid=%s&cid=%s&qn=%s&type=&otype=json&fourk=1"
    dmApi = "https://api.bilibili.com/x/v1/dm/list.so?oid=%s"

    def __init__(self, bid):
        self.bid = bid
        self.pages = []
        self.title = ""
        self.uploader = ""
        self.cover = ""
        self.currentPage = 1
        self.status = 200

    @property
    def id(self):
        return self.bid

    @classmethod
    def applicable(cls, url):
        return re.search(cls.patternAv, url) != None or re.search(cls.patternBv, url) != None

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
    def initFromData(cls, id, title, uploader, cover, pages):
        v = cls.initFromId(id)
        v.title = title
        v.uploader = uploader
        v.cover = cover
        v.pages = pages
        return v

    def getPages(self):
        data = httpGet(self.pagesApi % self.bid)
        if data == None or data.json()["code"] != 0:
            return
        self.pages = [{"page": d["page"], "pagename": d["part"], "cid": d["cid"]} for d in data.json()["data"]]

    def getInfo(self, **kwargs):
        data = httpGet(self.detailApi % self.bid)
        if data == None: return
        data = data.json()
        try:
            self.title = data["data"]["View"]["title"]
            self.uploader = data["data"]["View"]["owner"]["name"]
            self.cover = data["data"]["View"]["pic"]
            self.getPages()
        except:
            pass

    def getPageCid(self, page):
        cid = 0
        for p in self.pages:
            if p["page"] == page:
                cid = p["cid"]
                break
        return cid

    def getPageName(self, page):
        pn = ""
        for p in self.pages:
            if p["page"] == page:
                pn = p["pagename"]
                break
        return pn

    def getQualities(self, page=1):
        quality = {}
        cid = self.getPageCid(page)
        if cid == 0:
            return quality
        data = httpGet(self.playurlApi % (self.bid, cid, 32))
        if data == None:
            return quality
        data = data.json()
        formats = data["data"]["accept_format"].split(",")
        for index, qn in enumerate(data["data"]["accept_quality"]):
            quality[qn] = (formats[index], data["data"]["accept_description"][index])
        return quality

    def getPlayurl(self, page=0, qn=116):
        urls = []
        if page == 0:
            page = self.currentPage
        cid = self.getPageCid(page)
        if cid == 0:
            return None
        data = httpGet(self.playurlApi % (self.bid, cid, qn), headers=Config.commonHeaders,
                       cookies=Config.commonCookies)
        if data == None:
            return None
        data = data.json()
        if (data["code"] != 0):
            return None
        for u in data["data"]["durl"]:
            urls.append(u["url"])
            if u["backup_url"] != None:
                urls.append(u["backup_url"])
        return {"qn": data["data"]["quality"], "format": data["data"]["format"], "urls": urls}

    def download(self, page=0, qn=116, video=True, damu=False, cover=False, all=False, downloader=None, **kwargs):
        if page == 0:
            page = self.currentPage
        if not self.isValid(): return
        if downloader == None:
            return
        if all:
            self.downloadAll(qn,video,damu,cover,downloader,**kwargs)
            return
        if video:
            data = self.getPlayurl(page=page, qn=qn)
            if len(data["urls"]) == 0:
                return
            url = data["urls"][0]
            suffix = url.split("?")[0].split(".")[-1]
            downloader.download(url, Config.saveroute, self.outputTitle("video", page, suffix),
                                headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.bid,
                                         "user-agent": Config.commonHeaders["user-agent"]})
        if cover:
            suffix = self.cover.split("?")[0].split(".")[-1]
            downloader.download(self.cover, Config.saveroute, self.outputTitle("cover", page, suffix),
                                headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.bid,
                                         "user-agent": Config.commonHeaders["user-agent"]})
        if damu:
            downloaders["requests"]().download(self.dmApi % self.getPageCid(page), Config.saveroute,
                                               self.outputTitle("damu", page, "xml"))


    def downloadAll(self,qn,video,damu,cover,downloader, **kwargs):
        if cover:
            suffix = self.cover.split("?")[0].split(".")[-1]
            downloader.download(self.cover, Config.saveroute, self.outputTitle("cover", 1, suffix),
                                headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.bid,
                                         "user-agent": Config.commonHeaders["user-agent"]})
        for page in range(1,len(self.pages)+1):
            if video:
                data = self.getPlayurl(page=page, qn=qn)
                if len(data["urls"]) == 0:
                    return
                url = data["urls"][0]
                suffix = url.split("?")[0].split(".")[-1]
                downloader.download(url, Config.saveroute, self.outputTitle("video", page, suffix),
                                    headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.bid,
                                             "user-agent": Config.commonHeaders["user-agent"]})
            if damu:
                downloaders["requests"]().download(self.dmApi % self.getPageCid(page), Config.saveroute,
                                                   self.outputTitle("damu", page, "xml"))

    def outputTitle(self, type, page, suffix):
        if (type == "video"):
            if (len(self.pages) > 1):
                return ".".join(
                    ["%s (P%s %s) - %s" % (self.title, page, self.getPageName(page), self.uploader), suffix])
            else:
                return ".".join([self.title + " - " + self.uploader, suffix])
        if (type == "cover"):
            return ".".join([self.title, suffix])
        if (type == "damu"):
            if (len(self.pages) > 1):
                return ".".join(["%s (P%s %s) - %s" % (self.title, page, self.getPageName(page), self.uploader), "xml"])
            else:
                return ".".join([self.title + " - " + self.uploader, "xml"])

    def dumpInfo(self):
        qs = "\n"
        for key, value in self.getQualities().items():
            qs += "%s: %s(%s)\n" % (key, value[1], value[0])
        return [("Type", self.name),
                ("Title", self.title),
                ("Uploader", self.uploader),
                ("Available Qualities", qs),
                ("Total page",
                 str(len(self.pages)) + "\n" + "\n".join("P%s - %s" % (x["page"], x["pagename"]) for x in self.pages))
                ]

    def isValid(self):
        if self.status == 404: return False
        return True if len(self.pages) > 0 else False


class biliBangumi(biliVideo):
    name = "bangumi"

    patterns = [r"ep[0-9]+",
                r"ss[0-9]+"]

    bangumiUrl = "https://www.bilibili.com/bangumi/play/%s"
    playurlApi = "https://api.bilibili.com/pgc/player/web/playurl?avid=&bvid=%s&cid=%s&qn=%s&type=&otype=json&fourk=1"

    def __init__(self, bid):
        super(biliBangumi, self).__init__(bid)

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

    def getQualities(self, page=1):
        quality = {}
        cid = self.getPageCid(page)
        if cid == 0:
            return quality
        data = httpGet(self.playurlApi % (self.bid, cid, 32))
        if data == None:
            return quality
        data = data.json()
        formats = data["result"]["accept_format"].split(",")
        for index, qn in enumerate(data["result"]["accept_quality"]):
            quality[qn] = (formats[index], data["result"]["accept_description"][index])
        return quality

    def getPlayurl(self, page=0, qn=116):
        urls = []
        if page == 0:
            page = self.currentPage
        cid = self.getPageCid(page)
        if cid == 0:
            return None
        data = httpGet(self.playurlApi % (self.bid, cid, qn), headers=Config.commonHeaders,
                       cookies=Config.commonCookies)
        if data == None:
            return None
        data = data.json()
        if (data["code"] != 0):
            return None
        for u in data["result"]["durl"]:
            urls.append(u["url"])
            if u["backup_url"] != None:
                urls.append(u["backup_url"])
        return {"qn": data["result"]["quality"], "format": data["result"]["format"], "urls": urls}

    def getInfo(self, **kwargs):
        if self.bid == "":
            return
        url = self.bangumiUrl % self.bid
        rawhtml = httpGet(url)
        if rawhtml == None:
            return
        try:
            rawhtml = rawhtml.text
            initial_state = json.loads(re.search(r"__INITIAL_STATE__={(.*?)]};", rawhtml).group()[18:-1])
            self.title = initial_state["mediaInfo"]["title"]
            self.cover = "https:" + initial_state["mediaInfo"]["cover"]
            eplist = initial_state["epList"]
            self.bid = eplist[0]["bvid"]
            self.currentPage = 1
            pages = []
            epid = ""
            if "ep" in url:
                epid = str(re.search(r"ep[0-9]+", url).group()[2:])
            for index, ep in enumerate(eplist, start=1):
                pages.append(
                    {"page": index, "pagename": "%s %s" % (ep["titleFormat"], ep["longTitle"]), "cid": ep["cid"]})
                if epid == str(ep["id"]):
                    self.currentPage = index
            self.pages = pages
        except Exception as e:
            print(repr(e))
            pass

    def outputTitle(self, type, page, suffix):
        if (type == "video"):
            return ".".join(["%s: %s" % (self.title, self.getPageName(page)), suffix])
        if (type == "cover"):
            return ".".join([self.title, suffix])
        if (type == "damu"):
            return ".".join(["%s: %s" % (self.title, self.getPageName(page)), suffix])

    def dumpInfo(self):
        qs = "\n"
        for key, value in self.getQualities().items():
            qs += "%s : %s(%s)\n" % (key, value[1], value[0])
        return [("Type", self.name),
                ("Title", self.title),
                ("Current Episode", self.getPageName(self.currentPage)),
                ("Available Qualities", qs),
                ("Total page", str(len(self.pages)) + "\n" + "\n".join(x["pagename"] for x in self.pages))
                ]


class biliVideoList():
    name = "videolist"

    pattern = r"fid=[0-9]+"

    # favApi = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
    favApi = "https://api.bilibili.com/x/v3/fav/resource/list?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
    # addApi = "https://api.bilibili.com/medialist/gateway/coll/resource/deal"
    addApi = "https://api.bilibili.com/x/v3/fav/resource/deal"

    downloadable = True
    watchable = False

    def __init__(self, media_id):
        self.media_id = media_id
        self.videos = []

    @property
    def id(self):
        return self.media_id

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    @classmethod
    def initFromUrl(cls, url):
        pattern = r"fid=[0-9]+"
        return cls(re.search(pattern, url).group()[4::]) if re.search(pattern, url) != None else cls("")

    def getInfo(self, maxNum=1000, **kwargs):
        self.clearData()
        pn = 1
        num = 0
        while True:
            data = httpGet(self.favApi % (self.media_id, pn), cookies=Config.commonCookies,
                           headers=Config.commonHeaders)
            if data == None: return
            data = data.json()
            if data["data"]["info"]["media_count"] == 0:
                break
            for media in data["data"]["medias"]:
                if num >= maxNum:
                    return
                bid = media["bvid"]
                title = media["title"]
                cover = media["cover"]
                uploader = media["upper"]["name"]
                # pages = [{"page": p["page"], "pagename": p["title"], "cid": p["id"]} for p in media["pages"]]
                v = biliVideo.initFromData(bid, title, uploader, cover, [])
                if media["attr"] == 0:
                    v.getPages()
                else:
                    v.status = 404
                self.videos.append(v)
                num += 1
            pn += 1

    def clearData(self):
        self.videos.clear()

    def download(self, downloader=None, **kwargs):
        if not self.isValid(): return
        if downloader == None:
            return
        video: biliVideo
        for video in self.videos:
            video.download(downloader=downloader, **kwargs)

    def dumpInfo(self):
        return [("Type", self.name),
                ("Media_id", self.media_id),
                ("Videoo number", len(self.videos))
                ]

    def isValid(self):
        return True if len(self.videos) > 0 else False

    def addVideo(self, aid):
        data = httpPost(self.addApi,
                        headers={"origin": "https://www.bilibili.com", "referer": "https://www.bilibili.com"},
                        cookies=Config.commonCookies,
                        data={'rid': int(aid), 'type': 2, 'add_media_ids': int(self.media_id), 'del_media_ids': "",
                              'jsonp': 'jsonp'})
        return data.json() if data != None else None
