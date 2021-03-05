from apis import JsonResponseContainer
from sources.base import MediaSource, PictureSource, TextSource, CommonSource,SearchResult,SearchResults
from sources.base.interface import SearchableSource
from utils.vhttp import httpGet
from sources.bilibili import BilibiliSource
from config import Config
import apis.bilibili.audio as baudioApi
import apis.bilibili.audiolist as balApi
import re,random

class biliAudio(BilibiliSource,SearchableSource):
    __source_name__ = "audio"

    pattern = r"au[0-9]+"

    base_url = "https://www.bilibili.com/audio/"

    headers = {"user-agent": "BilibiliClient/2.33.3",
               'Accept': "*/*",
               'Connection': "keep-alive"}

    @classmethod
    @CommonSource.wrapper.handleException
    def search(cls, keyword, page=1,pagesize=5, **kwargs) -> SearchResults:

        container = JsonResponseContainer(baudioApi.getSearchResult(keyword,
                                                                    page= page,
                                                                    pagesize=pagesize),
                                          currentpage = "data.page",
                                          totalpage = "data.num_pages",
                                          result = "data.result")
        cp,tp,result = container.data["currentpage"],container.data["totalpage"],container.data["result"]
        rs = []
        for r in result:
            bas = cls(r["id"])
            bas.title = r["title"]
            bas.author =r["author"]
            bas.uploader = r["up_name"]
            bas.cover_url = r["cover"]
            rs.append(SearchResult("{baseurl}au{id}".format(baseurl = cls.base_url,
                                                            id = r["id"]),
                                   cls.headers,
                                   "{title} - {author} - {up}".format(title = r["title"],
                                                                      author = r["author"],
                                                                      up = r["up_name"]),
                                   bas,
                                   cls.getSourceName(),
                                   "audio"))
        return SearchResults(rs,cp,tp)

    def __init__(self, sid):
        self.sid = sid
        self.title = ""
        self.author = ""
        self.uploader = ""
        self.lyric_url = ""
        self.cover_url = ""

    @property
    def id(self):
        return self.sid

    @property
    def audio(self):
        return self.getAudio()

    @CommonSource.wrapper.handleException
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
        qs = ["%s: %s(%s %s)" % (key,value[2],value[0],value[1]) for key,value in self._getQualities().items()]
        return {"Type":self.getSourceName(),
                "Title":self.title,
                "Uploader":self.uploader,
                "Available Qualities":qs}

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

    @CommonSource.wrapper.handleException
    def load(self,**kwargs):
        container = JsonResponseContainer(baudioApi.getAudioInfo(self.sid),
                                          title = "data.title",
                                          uploader = "data.uname",
                                          author = "data.author",
                                          lyric = "data.lyric",
                                          cover = "data.cover")
        self.title = container.data["title"]
        self.uploader = container.data["uploader"]
        self.author = container.data["author"]
        self.lyric_url = container.data["lyric"]
        self.cover_url = container.data["cover"]

    def _getQualities(self):
        quality = {}
        container = JsonResponseContainer(baudioApi.getAudioFile(self.sid, quality=2),
                                          qualities="data.qualities")
        for q in container.data["qualities"]:
           quality[q["type"]] = (q["tag"], q["bps"] ,q["desc"])
        return quality

    def _getCdns(self, quality=2):
        container = JsonResponseContainer(baudioApi.getAudioFile(self.sid,quality=quality),
                                          cdns = "data.cdns")
        return container.data["cdns"]

    def getBaseSources(self,qn=2,**kwargs):
        if not self.isValid(): return {}
        return {"audio":self.getAudio(qn=qn),
                "lyric":self.lyric,
                "cover":self.cover}

    def isValid(self):
        return True if self.title != "" else False

class biliAudioList(BilibiliSource):
    __source_name__ = "audiolist"

    pattern = r"am[0-9]+"


    def __init__(self, sid):
        self.sid = sid
        self.audios = []

    @property
    def id(self):
        return self.sid

    @property
    def info(self):
        return {"Type": self.getSourceName(),
                "Audio number": len(self.audios)}

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern, url) != None

    @classmethod
    def initFromUrl(cls, url):
        pattern = "am[0-9]+"
        return cls(re.search(pattern, url).group()[2::]) if re.search(pattern, url) != None else cls("")

    @CommonSource.wrapper.handleException
    def load(self,maxNum=1000,**kwargs):
        self.audios.clear()
        num = 0
        pn = 1
        while True:
            container = JsonResponseContainer(balApi.getAudioListInfo(self.sid,
                                                                      page = pn),
                                              data = "data.data",
                                              curpage = "data.curPage",
                                              totalpage = "data.pageCount")
            for audio in container.data["data"]:
                if num >= maxNum: return
                self.audios.append(biliAudio.initFromData(audio["id"],
                                                          audio["title"],
                                                          audio["author"],
                                                          audio["lyric"],
                                                          audio["cover"]))
                num +=1
            if container.data["curpage"] == container.data["totalpage"]:
                break
            pn += 1

    def getBaseSources(self,**kwargs):
        if not self.isValid(): return {}
        audio: biliAudio
        return {"audio":[audio.getBaseSources(**kwargs) for audio in self.audios]}

    def isValid(self):
        return True if len(self.audios) > 0 else False