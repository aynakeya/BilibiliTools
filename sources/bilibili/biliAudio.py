from sources.base import MediaSource,PictureSource,TextSource
from utils.http import httpGet
from sources.bilibili import BilibiliSource
from config import Config

import re,random

class biliAudio(BilibiliSource):
    name = "audio"

    pattern = r"au[0-9]+"

    fileApi = "http://api.bilibili.com/audio/music-service-c/url?mid=8047632&mobi_app=iphone&platform=ios&privilege=2&quality=%s&songid=%s"
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/info?sid=%s"
    headers = {"user-agent": "BilibiliClient/2.33.3",
               'Accept': "*/*",
               'Connection': "keep-alive"}

    downloadable = True
    watchable = True

    def __init__(self, sid):
        self.sid = sid
        self.title = ""
        self.uploader = ""
        self.lyric_url = ""
        self.cover_url = ""

    @property
    def id(self):
        return self.sid

    @property
    def audio(self):
        return self.getAudio()

    def getAudio(self,qn=2):
        cdns = self._getCdns(quality=qn)
        if len(cdns) != 0:
            url = random.choice(cdns)
            suffix = url.split("?")[0].split(".")[-1]
            return MediaSource(url, self.headers, ".".join([self.title, suffix]))

    @property
    def lyric(self):
        if self.lyric_url != "":
            suffix = self.lyric_url.split("?")[0].split(".")[-1]
            return TextSource(self.lyric_url,{},".".join([self.title, suffix]),"")

    @property
    def cover(self):
        if self.cover_url != "":
            suffix = self.cover_url.split("?")[0].split(".")[-1]
            return PictureSource(self.cover_url, {}, ".".join([self.title, suffix]), "")

    @property
    def info(self):
        qs = ""
        for key,value in self._getQualities().items():
            qs += "%s: %s(%s %s)\n" % (key,value[2],value[0],value[1])
        return [("Type",self.name),
                ("Title",self.title),
                ("Uploader",self.uploader),
                ("Available Qualities",qs)]

    @classmethod
    def applicable(cls,url):
        return re.search(cls.pattern,url) != None

    @classmethod
    def initFromUrl(cls, url):
        pattern = r"au[0-9]+"
        return cls(re.search(pattern, url).group()[2::]) if re.search(pattern, url) !=None else cls("")

    @classmethod
    def initFromData(cls, sid,title,uploader,lyric_url,cover_url):
        v = cls(sid)
        v.title = title
        v.uploader = uploader
        v.lyric_url = lyric_url
        v.cover_url = cover_url
        return v

    def load(self,**kwargs):
        data = httpGet(self.infoApi % self.sid, headers=self.headers)
        if data == None:
            return
        data = data.json()
        try:
            self.title = data["data"]["title"]
            self.uploader = data["data"]["author"]
            self.lyric_url = data["data"]["lyric"]
            self.cover_url = data["data"]["cover"]
        except:
            pass

    def _getQualities(self):
        quality = {}
        data = httpGet(self.fileApi % ("2", self.sid), headers=self.headers)
        if data == None:
            return quality
        data = data.json()
        for q in data["data"]["qualities"]:
           quality[q["type"]] = (q["tag"], q["bps"] ,q["desc"])
        return quality

    def _getCdns(self, quality=2):
        data = httpGet(self.fileApi % (quality, self.sid), headers=self.headers)
        return [] if data==None else data.json()["data"]["cdns"]

    def getBaseSources(self,qn=2,**kwargs):
        if not self.isValid(): return {}
        return {"audio":self.getAudio(qn=qn),
                "lyric":self.lyric,
                "cover":self.cover}

    def isValid(self):
        return True if self.title != "" else False

class biliAudioList(BilibiliSource):
    name = "audiolist"

    pattern = r"am[0-9]+"
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?ps=100&sid=%s&pn=%s"

    downloadable = True
    watchable = False

    def __init__(self, sid):
        self.sid = sid
        self.audios = []

    @property
    def id(self):
        return self.sid

    @property
    def info(self):
        return [("Type", self.name),
                ("Audio number", len(self.audios))]

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    @classmethod
    def initFromUrl(cls, url):
        pattern = "am[0-9]+"
        return cls(re.search(pattern, url).group()[2::]) if re.search(pattern, url) != None else cls("")

    def load(self,maxNum=1000,**kwargs):
        self.audios.clear()
        num = 0
        pn = 1
        while True:
            data = httpGet(self.infoApi % (self.sid, pn), headers = Config.commonHeaders)
            if data == None: return
            data = data.json()
            for audio in data["data"]["data"]:
                if num >= maxNum: return
                self.audios.append(biliAudio.initFromData(audio["id"],
                                                          audio["title"],
                                                          audio["author"],
                                                          audio["lyric"],
                                                          audio["cover"]))
                num +=1
            if data["data"]["pageCount"] == data["data"]["curPage"]:
                break
            pn += 1

    def getBaseSources(self,**kwargs):
        if not self.isValid(): return {}
        audio: biliAudio
        return {"audio":[audio.getBaseSources(**kwargs) for audio in self.audios]}

    def isValid(self):
        return True if len(self.audios) > 0 else False