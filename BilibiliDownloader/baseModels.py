from pyaria2 import Aria2RPC
import os, re, random
import requests

def filenameparser(filename):
    pattern = r'[\\/:*?"<>|\r\n]+'
    return re.sub(pattern,"-",filename)

def httpConnect(url, maxReconn=5, **kwargs):
    trial = 0
    while trial < maxReconn:
        try:
            return requests.get(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None

class Config:
    proxies = {}
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    commonCookies = {
                     "SESSDATA":"6d15a145%2C1570415616%2C9be00591",
    }
    saveroute = r"E:\Download\bilidown"

    aria2rpc = "http://localhost:6800/rpc"
    #if no token provide, using None
    aria2token = None

    defaultDownloader = "aria"

class ariaDownloader():
    def __init__(self, url=Config.aria2rpc, token=Config.aria2token):
        self.rpc = Aria2RPC(url=url, token=token)

    def parseHeader(self,headers):
        return ["%s:%s" % h for h in headers.items()]

    def download(self, url, route, filename, **kwargs):
        kwargs["dir"] = route
        kwargs["out"] = filenameparser(filename)
        if "headers" in kwargs.keys():
            kwargs["header"] = self.parseHeader(kwargs.pop("headers"))
        self.rpc.addUri([url], kwargs)

class simpleDownloader():
    def __init__(self):
        pass

    def download(self, url, route, filename,**kwargs):
        fn = filenameparser(filename)
        raw_data = httpConnect(url,**kwargs)
        if raw_data == None:
            return False
        path = os.path.join(route, fn)
        if not os.path.exists(route):
            os.mkdir(route)
        with open(path,"wb+") as f:
            f.write(raw_data.content)
        return True


aria = ariaDownloader()
simpled = simpleDownloader()

downloaders = {"aria":aria,
               "simple":simpled}

class biliVideo():
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


    def download(self,page=1,qn=116,video=True,damu=False,cover=False,downloader=Config.defaultDownloader,**kwargs):
        if not self.isValid():return
        dl = downloaders.get(downloader)
        if dl == None:
            return
        if video:
            data = self.getPlayurl(page=page, qn=qn)
            if len(data["urls"]) == 0:
                return
            url = data["urls"][0]
            suffix = url.split("?")[0].split(".")[-1]
            dl.download(url, Config.saveroute, ".".join([self.title + " - " + self.uploader, suffix]),
                        headers={"origin": "www.bilibili.com", "referer": self.videoUrl % self.aid,
                                 "user-agent": Config.commonHeaders["user-agent"]})
        if cover:
            suffix = self.cover.split("?")[0].split(".")[-1]
            dl.download(self.cover,Config.saveroute,".".join([self.title,suffix]),
                        headers={"origin": "www.bilibili.com", "referer": self.videoUrl % self.aid,
                                 "user-agent": Config.commonHeaders["user-agent"]})
        if damu:
            downloaders["simple"].download(self.dmApi % self.getPageCid(page),Config.saveroute,".".join([self.title,"xml"]))

    def isValid(self):
        if self.status == 404: return False
        return True if len(self.pages) > 0 else False

class biliVideoList():
    favApi = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
    def __init__(self,media_id):
        self.media_id = media_id
        self.videos = []

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

    def download(self,downloader=Config.defaultDownloader,**kwargs):
        if not self.isValid(): return
        video: biliVideo
        for video in self.videos:
            df = video.download(downloader=downloader,**kwargs)

    def isValid(self):
        return True if len(self.videos) > 0 else False

class biliAudio(object):
    fileApi = "http://api.bilibili.com/audio/music-service-c/url?mid=8047632&mobi_app=iphone&platform=ios&privilege=2&quality=%s&songid=%s"
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/info?sid=%s"
    headers = {"user-agent": "BilibiliClient/2.33.3",
               'Accept': "*/*",
               'Connection': "keep-alive"}

    def __init__(self, sid):
        self.sid = sid
        self.title = ""
        self.uploader = ""
        self.lyric = ""
        self.cover = ""

    @classmethod
    def initFromUrl(cls, url):
        pattern = r"au[0-9]+"
        return cls(re.search(pattern, url).group()[2::]) if re.search(pattern, url) !=None else cls("")

    @classmethod
    def initFromData(cls, sid,title,uploader,lyric,cover):
        v = cls(sid)
        v.title = title
        v.uploader = uploader
        v.lyric = lyric
        v.cover = cover
        return v

    def getInfo(self,**kwargs):
        data = httpConnect(self.infoApi % self.sid, headers=self.headers)
        if data == None:
            return
        data = data.json()
        try:
            self.title = data["data"]["title"]
            self.author = data["data"]["author"]
            self.lyric = data["data"]["lyric"]
            self.cover = data["data"]["cover"]
        except:
            pass

    def getCdns(self, quality=2):
        data = httpConnect(self.fileApi % (quality, self.sid), headers=self.headers)
        return [] if data==None else data.json()["data"]["cdns"]

    def download(self,qn=2,audio=True,lyric=False,cover=False,downloader=Config.defaultDownloader,**kwargs):
        if not self.isValid(): return
        dl = downloaders.get(downloader)
        if dl == None:
            return
        if audio:
            cdns = self.getCdns(quality=qn)
            if len(cdns) != 0:
                url = random.choice(cdns)
                suffix = url.split("?")[0].split(".")[-1]
                dl.download(url,Config.saveroute,".".join([self.title,suffix]),headers=self.headers)
        if lyric:
            if self.lyric != "":
                suffix = self.lyric.split("?")[0].split(".")[-1]
                dl.download(self.lyric, Config.saveroute, ".".join([self.title, suffix]),
                              headers=self.headers)
        if cover:
            if self.cover != "":
                suffix = self.cover.split("?")[0].split(".")[-1]
                dl.download(self.cover, Config.saveroute,".".join([self.title, suffix]),
                              headers=self.headers)

    def isValid(self):
        return True if self.title != "" else False

class biliAudioList(object):
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?ps=100&sid=%s&pn=%s"

    def __init__(self, sid):
        self.sid = sid
        self.audio = []

    @classmethod
    def initFromUrl(cls, url):
        pattern = "am[0-9]+"
        return cls(re.search(pattern, url).group()[2::]) if re.search(pattern, url) != None else cls("")

    def getInfo(self,maxNum=1000,**kwargs):
        self.clearData()
        num = 0
        pn = 1
        api = self.infoApi % (self.sid, "%s")
        while True:
            data = httpConnect(self.infoApi %(self.sid,pn),headers = Config.commonHeaders)
            if data == None: return
            data = data.json()
            for audio in data["data"]["data"]:
                if num >= maxNum: return
                self.audio.append(biliAudio.initFromData(audio["id"],audio["title"],audio["author"],audio["lyric"],audio["cover"]))
                num +=1
            if data["data"]["pageCount"] == data["data"]["curPage"]:
                break
            pn += 1

    def clearData(self):
        self.audio.clear()

    def download(self, downloader=Config.defaultDownloader, **kwargs):
        if not self.isValid(): return
        audio: biliAudio
        for audio in self.audio:
            audio.download(downloader=downloader,**kwargs)


    def isValid(self):
        return True if len(self.audio)>0 else False

# v = biliVideo.initFromUrl("https://www.bilibili.com/video/av51266788")
# v.getInfo()
# v.download()
# v = biliVideo.initFromAid("45821878")
# v.getInfo()
# print(v.aid,v.title,v.pages,v.isValid())
#v.download()

# f = bilVideoList.initFromUrl("https://space.bilibili.com/10003632/favlist?fid=278832132&ftype=create")
#
# f.getInfo(2)
# for v in f.videos:
#     print(v.aid,v.title,v.pages,v.isValid())
# f.download(downloader="simple",video=False,damu=True)

# a = biliAudio.initFormUrl("https://www.bilibili.com/audio/au295140?type=3")
# print(a.sid)
# a.getInfo()
# a.download(cover=True,lyric=True,downloader="aria")

# al = biliAudioList.initFromUrl("https://www.bilibili.com/audio/am10624?type=2")
# al.getInfo()
# for a in al.audio:
#     print(a.sid,a.title,a.uploader)
# al.download(audio=False,cover=True)