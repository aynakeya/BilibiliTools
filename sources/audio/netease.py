import re

from config import Config
from sources import SearchResults, CommonSource, MediaSource, SearchResult
from sources.audio import AudioSource
from sources.base.interface import SearchableSource
from pyncm.apis import track,cloudsearch

from utils import file


class NeteaseMusicSource(AudioSource,
                         SearchableSource):
    name = "netease-audio"

    base_url = "https://music.163.com/"

    song_url = "https://music.163.com/#/song?id={id}"

    pattern = r"music\.163\.com/\#/song\?id=[0-9]+"
    patternB = r"163audio[0-9]+"

    @classmethod
    def search(cls, keyword, pagesize= 10,*args, **kwargs) -> SearchResults:
        data = cloudsearch.GetSearchResult(keyword,limit=pagesize,offset=0)
        if data["result"]["songCount"] == 0:
            return SearchResults([],0,0)
        results = []
        for song in data["result"]["songs"]:
            ns = cls(song["id"])
            ns.cover_url = song["id"]
            ns.artists = [ar["name"] for ar in song["ar"]]
            ns.vip = bool(song["fee"])
            ns.title = song["name"]
            results.append(SearchResult(cls.song_url.format(id=song["id"]),
                                        {},
                                        ns._getParsedTitle(),
                                        ns,
                                        cls.getSourceName(),
                                        "audio"))
        return SearchResults(results,1,1)

    def __init__(self,sid):
        self.sid = sid
        self.cover_url = ""
        self.artists = ""
        self.title = ""
        self.vip = False

    @property
    def audio(self):
        return self.getAudio()

    @CommonSource.wrapper.handleException
    def getAudio(self):
        data = track.GetTrackAudio(self.sid)
        url = data["data"][0]["url"]
        return MediaSource(data["data"][0]["url"],
                           Config.commonHeaders,
                           "{}.{}".format(self._getParsedTitle(),file.getSuffixByUrl(url)))

    def isValid(self):
        return self.sid != "" and self.title != ""

    @classmethod
    def initFromUrl(cls, url:str):
        if (url.isdigit()):
            return cls(url)
        id = re.search(r"id=[0-9]+",url)
        if id == None: return cls("")
        return cls(id.group()[3::])

    @property
    def info(self):
        return {"Type": self.getSourceName(),
                "Title": self.title,
                "Vip": "Yes" if self.vip else "No",
                "Artists": ",".join(self.artists)}

    def getBaseSources(self,*args,**kwargs):
        return {"audio":self.getAudio()}

    @CommonSource.wrapper.handleException
    def load(self,*args,**kwargs):
        data = track.GetTrackDetail(self.sid)
        self.artists = [ar["name"] for ar in data["songs"][0]["ar"]]
        self.cover_url = data["songs"][0]["al"]["picUrl"]
        self.vip = bool(data["songs"][0]["fee"])
        self.title = data["songs"][0]["name"]

    @classmethod
    def applicable(cls, url):
        return re.search(cls.pattern,url) != None or re.search(cls.patternB,url) != None

    def _getParsedTitle(self):
        return "{title} - {artists}".format(title = self.title,
                                            artists = ",".join(self.artists))



# a = NeteaseAudioSource.initFromUrl("536570450")
# a.load()
# print(a.info)
# a.getAudio()
# if __name__ == "__main__":
#     NeteaseMusicSource.search("so cute~asdvadsfy34fasfasf")
