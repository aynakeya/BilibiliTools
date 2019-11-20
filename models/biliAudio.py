from utils import httpConnect,filenameparser
from config import Config
import re,random

class biliAudio(object):
    name = "audio"

    pattern = r"au[0-9]+"

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
    def applicable(cls,url):
        return re.search(cls.pattern,url) != None

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

    def download(self,downloader=None,qn=2,audio=True,lyric=False,cover=False,**kwargs):
        if not self.isValid(): return
        if downloader == None:
            return
        if audio:
            cdns = self.getCdns(quality=qn)
            if len(cdns) != 0:
                url = random.choice(cdns)
                suffix = url.split("?")[0].split(".")[-1]
                downloader.download(url,Config.saveroute,".".join([self.title,suffix]),headers=self.headers)
        if lyric:
            if self.lyric != "":
                suffix = self.lyric.split("?")[0].split(".")[-1]
                downloader.download(self.lyric, Config.saveroute, ".".join([self.title, suffix]),
                              headers=self.headers)
        if cover:
            if self.cover != "":
                suffix = self.cover.split("?")[0].split(".")[-1]
                downloader.download(self.cover, Config.saveroute,".".join([self.title, suffix]),
                              headers=self.headers)

    def isValid(self):
        return True if self.title != "" else False

class biliAudioList(object):
    name = "audiolist"

    pattern = r"am[0-9]+"
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?ps=100&sid=%s&pn=%s"

    def __init__(self, sid):
        self.sid = sid
        self.audio = []

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

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

    def download(self, downloader=None, **kwargs):
        if downloader == None:
            return
        if not self.isValid(): return
        audio: biliAudio
        for audio in self.audio:
            audio.download(downloader=downloader,**kwargs)


    def isValid(self):
        return True if len(self.audio)>0 else False