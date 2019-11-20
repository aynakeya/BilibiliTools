from utils import httpConnect,filenameparser
from config import Config
from downloaders import downloaders
import re,random

class biliVideo():
    name = "video"

    pattern = r"av[0-9]+"

    videoUrl = "https://www.bilibili.com/video/av%s"
    pagesApi = "https://www.bilibili.com/widget/getPageList?aid=%s"
    detailApi = "https://api.bilibili.com/x/web-interface/view/detail?aid=%s&jsonp=jsonp"
    playurlApi = "https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=%s&type=&otype=json"
    dmApi = "https://api.bilibili.com/x/v1/dm/list.so?oid=%s"

    def __init__(self,aid):
        self.aid = aid
        self.pages = []
        self.title = ""
        self.uploader = ""
        self.cover = ""
        self.status = 200

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    @classmethod
    def initFromAid(cls,aid):
        v = cls(aid)
        return v

    @classmethod
    def initFromUrl(cls,url):
        pattern = r"av[0-9]+"
        return cls(re.search(pattern,url).group()[2::]) if re.search(pattern,url) !=None else cls("")

    @classmethod
    def initFromData(cls, aid, title, uploader, cover, pages):
        v = cls(aid)
        v.title = title
        v.uploader = uploader
        v.cover = cover
        v.pages = pages
        return v

    def getPages(self):
        data = httpConnect(self.pagesApi % self.aid)
        if data == None:
            return
        self.pages = data.json()

    def getInfo(self,**kwargs):
        data = httpConnect(self.detailApi % self.aid)
        if data == None: return
        data = data.json()
        try:
            self.title = data["data"]["View"]["title"]
            self.uploader = data["data"]["View"]["owner"]["name"]
            self.cover = data["data"]["View"]["pic"]
            self.getPages()
        except:
            pass
    def getPageCid(self,page):
        cid = 0
        for p in self.pages:
            if p["page"] == page:
                cid = p["cid"]
                break
        return cid

    def getQualities(self,page=1):
        quality = {}
        cid = self.getPageCid(page)
        if cid == 0:
            return quality
        data = httpConnect(self.playurlApi % (self.aid, cid, 32))
        if data == None:
            return quality
        data = data.json()
        formats = data["data"]["accept_format"].split(",")
        for index,qn in enumerate(data["data"]["accept_quality"]):
            quality[qn] = (formats[index],data["data"]["accept_description"][index])
        return quality

    def getPlayurl(self,page=1,qn=116):
        urls = []
        cid = self.getPageCid(page)
        if cid == 0:
            return {}
        data = httpConnect(self.playurlApi % (self.aid, cid, qn),headers = Config.commonHeaders,cookies=Config.commonCookies)
        if data == None:
            return {}
        data = data.json()
        for u in data["data"]["durl"]:
            urls.append(u["url"])
            if u["backup_url"] != None:
                urls.append(u["backup_url"])
        return {"qn":data["data"]["quality"],"format":data["data"]["format"],"urls":urls}


    def download(self,page=1,qn=116,video=True,damu=False,cover=False,downloader=None,**kwargs):
        if not self.isValid():return
        if downloader == None:
            return
        if video:
            data = self.getPlayurl(page=page, qn=qn)
            if len(data["urls"]) == 0:
                return
            url = data["urls"][0]
            suffix = url.split("?")[0].split(".")[-1]
            downloader.download(url, Config.saveroute, ".".join([self.title + " - " + self.uploader, suffix]),
                        headers={"origin": "www.bilibili.com", "referer": self.videoUrl % self.aid,
                                 "user-agent": Config.commonHeaders["user-agent"]})
        if cover:
            suffix = self.cover.split("?")[0].split(".")[-1]
            downloader.download(self.cover,Config.saveroute,".".join([self.title,suffix]),
                        headers={"origin": "www.bilibili.com", "referer": self.videoUrl % self.aid,
                                 "user-agent": Config.commonHeaders["user-agent"]})
        if damu:
            downloaders["requests"]().download(self.dmApi % self.getPageCid(page),Config.saveroute,".".join([self.title,"xml"]))

    def isValid(self):
        if self.status == 404: return False
        return True if len(self.pages) > 0 else False

class biliVideoList():
    name = "videolist"

    pattern = r"fid=[0-9]+"

    favApi = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
    def __init__(self,media_id):
        self.media_id = media_id
        self.videos = []

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    @classmethod
    def initFromUrl(cls,url):
        pattern = r"fid=[0-9]+"
        return cls(re.search(pattern, url).group()[4::]) if re.search(pattern, url) != None else cls("")

    def getInfo(self,maxNum=1000,**kwargs):
        self.clearData()
        pn = 1
        num = 0
        while True:
            data = httpConnect(self.favApi%(self.media_id,pn),headers=Config.commonHeaders)
            if data == None:return
            data = data.json()
            if data["data"]["info"]["media_count"] == 0:
                break
            for media in data["data"]["medias"]:
                if num >= maxNum:
                    return
                aid = media["id"]
                title = media["title"]
                cover = media["cover"]
                uploader = media["upper"]["name"]
                pages = [{"page":p["page"],"pagename":p["title"],"cid":p["id"]} for p in media["pages"]]
                v = biliVideo.initFromData(aid, title, uploader, cover, pages)
                if media["attr"] == 9:
                    v.status = 404
                self.videos.append(v)
                num +=1
            pn +=1

    def clearData(self):
        self.videos.clear()

    def download(self,downloader=None,**kwargs):
        if not self.isValid(): return
        if downloader == None:
            return
        video: biliVideo
        for video in self.videos:
            video.download(downloader=downloader,**kwargs)

    def isValid(self):
        return True if len(self.videos) > 0 else False