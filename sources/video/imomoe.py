import traceback
from config import Config
from sources import MediaSource, CommonSource
from sources.base.SearchResult import SearchResult, SearchResults
from sources.base.interface import SearchableSource
from sources.video import VideoSource
from utils import file, formats
from bs4 import BeautifulSoup
from urllib import parse
import re, json

from utils.vhttp import httpGet


class ImomoeSource(VideoSource, SearchableSource):
    name = "imomoe"

    base_url = "http://www.imomoe.ai/"
    player_url = "http://www.imomoe.ai/player/{id}.html"
    real_src_api = "https://api.xiaomingming.org/cloud/mp6.php?vid={src}"
    id_format = "{id}-{sid}-{ep_id}"

    patternA = r"imomoe\.ai\/player\/(.*)\.html"
    patternB = r"imomoe\.ai\/view\/(.*)\.html"

    search_api = "http://www.imomoe.ai/search.asp?searchword={keyword}&page={page}"

    @classmethod
    @CommonSource.wrapper.handleException
    def search(cls, keyword, page=1, *args, **kwargs):
        url = cls.search_api.format(keyword=parse.quote(keyword, encoding="gb2312"),
                                    page=page)
        html_text = formats.htmlAutoDecode(httpGet(url).content)
        pg = re.search(r"页次:[0-9]+/[0-9]+页", html_text)
        if pg == None:
            return None
        pagenum = pg.group()[3:-1:].split("/")
        cp, tp = int(pagenum[0]), int(pagenum[1])
        soup = BeautifulSoup(html_text, "html.parser")
        rs = []
        for li in soup.find("div", {"class": "pics"}).find_all("li"):
            rs.append(SearchResult(cls.base_url + li.a["href"][1::],
                                   Config.commonHeaders,
                                   li.h2.a["title"],
                                   cls.getSourceName(),
                                   "video"))
        return SearchResults(rs, cp, tp)

    def __init__(self, id, source_id, ep_id):
        self.id = id
        self.source_id = source_id
        self.ep_id = ep_id
        self.title = ""
        self.episodes = {}

    @classmethod
    def initFromUrl(cls, url):
        if re.search(cls.patternA, url) != None:
            url = re.search(cls.patternA, url).group()
            url = url.replace("imomoe.ai/player/", "").replace(".html", "")
            ids = url.split("-")
            return cls(ids[0], ids[1], ids[-1])
        elif re.search(cls.patternB, url) != None:
            url = re.search(cls.patternB, url).group()
            url = url.replace("imomoe.ai/view/", "").replace(".html", "")
            return cls(url, "0", "0")
        return cls("", "", "")

    @classmethod
    def applicable(cls, url):
        return re.search(cls.patternA, url) != None or re.search(cls.patternB, url) != None

    @property
    def info(self):
        return {"Type": self.name,
                "Title": self.title,
                "Episode Title": self.episodes[self.source_id][int(self.ep_id)]["title"],
                "Available Source":",".join(self.episodes.keys()),
                "Available episodes":["{index}: {title} [-eid={index}]".format(index = index,
                                                                               title = x["title"])
                                      for index,x in enumerate(self.episodes[self.source_id])]}

    @property
    def video(self):
        return self.getVideo()

    def isValid(self):
        return len(self.episodes.keys()) > 0

    def getBaseSources(self, sid="-1", eid="-1", all=False, **kwargs):
        if all:
            return {"video": [self.getVideo(source_id=self.source_id, ep_id=str(eid))
                              for eid in range(len(self.episodes[self.source_id]))]}
        else:
            return {"video": self.getVideo(source_id=sid, ep_id=eid)}

    @CommonSource.wrapper.handleException
    def getVideo(self, source_id: str = "-1", ep_id: str = "-1"):
        source_id, ep_id = str(source_id), str(ep_id)
        source_id = self.source_id if source_id == "-1" else source_id
        ep_id = self.ep_id if ep_id == "-1" else ep_id
        data = self.episodes[source_id][int(ep_id)]
        player_html = httpGet(self.real_src_api.format(src=data["src"])).content.decode("utf-8")
        real_url = re.search(
            "varvideo='(.*)';", player_html.replace(" ", "")).group()[10:-2:]
        return MediaSource(real_url, Config.commonHeaders,
                           "{}-{}.{}".format(self.title,
                                             data["title"],
                                             file.getSuffixByUrl(real_url)))

    @CommonSource.wrapper.handleExceptionNoReturn
    def load(self, **kwargs):
        raw_html = httpGet(self.player_url.format(id=self.id_format
                                                  .format(id=self.id, sid=self.source_id, ep_id=self.ep_id)))
        if raw_html == None: return
        html_text = formats.htmlAutoDecode(raw_html.content)
        self.title = re.search(r"xTitle='(.*)'", html_text).group()[8:-1:]
        playdata_url = re.search(r"src=\"/playdata/(.*)\"", html_text).group()[4:-1:]
        playdata = formats.htmlAutoDecode(httpGet(self.base_url + playdata_url[1::]).content)
        videolist = re.search(r"=\[(.*)\],", playdata).group()[1:-1:].replace("'", "\"")
        for index, part in enumerate(json.loads(videolist)):
            sid = str(index)
            self.episodes[sid] = []
            for url in part[1]:
                tmp = url.split("$")
                self.episodes[sid].append({"title": tmp[0],
                                           "src": tmp[1],
                                           "format": tmp[2]})

# if __name__ == "__main__":
#     a = ImomoeSource.search("dxd")
#     print(a.results)
#     print(a.current_page,a.total_page)
