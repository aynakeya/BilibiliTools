from utils import httpGet
from config import Config
import re


class biliLive():
    name = "live"

    patternUrl = r"live\.bilibili\.com\/[0-9]+"
    patternId = r"live[0-9]+"

    baseUrl = "https://live.bilibili.com/%s"

    downloadable = False
    watchable = True

    # from https://github.com/wbt5/real-url/blob/master/bilibili.py
    def __init__(self, rid):
        self.rid = rid
        self.room_id = ""
        self.title = "Bilibili Live %s" % rid

    @property
    def id(self):
        return self.rid

    @classmethod
    def applicable(cls, url):
        return bool(re.search(cls.patternUrl, url)) or bool(re.search(cls.patternId, url))

    def isValid(self):
        return self.room_id != ""

    def getInfo(self):
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id={}'.format(self.rid)
        res = httpGet(r_url).json()
        if res["code"] == 0:
            if res['data']['live_status'] == 1:
                self.room_id = res['data']['room_id']
        tp = r"<title id=\"link-app-title\">.*<\/title>"
        res = httpGet(self.baseUrl%self.rid,
                      headers={"origin": "www.bilibili.com", "referer": self.baseUrl % self.id,
                               "user-agent": Config.commonHeaders["user-agent"]}
                      ).content.decode("utf-8")
        if re.search(tp,res):
            self.title = re.search(tp, res).group()[27:-8:]

    @classmethod
    def initFromUrl(cls, url):
        if re.search(cls.patternUrl, url):
            return cls(re.search(cls.patternUrl, url).group()[18::])
        if re.search(cls.patternId, url):
            return cls(re.search(cls.patternId, url).group()[4::])
        return cls("")

    def _getRealUrlByPlatform(self,pf):
        f_url = 'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl'
        params = {
            'cid': self.room_id,
            'qn': 10000,
            'platform': pf,
            'https_url_req': 1,
            'ptype': 16
        }
        resp = httpGet(f_url, params=params).json()
        try:
            durl = resp['data']['durl']
            real_url = durl[-1]['url']
            return real_url
        except:
            return None

    def getRealUrl(self):
        if self.isValid():
            return {
                'flv_url': self._getRealUrlByPlatform('web'),
                'hls_url': self._getRealUrlByPlatform('h5')
            }
        return {
            'flv_url': None,
            'hls_url': None
        }

    def getPlayurl(self,format="hls"):
        fmts = {"hls":"h5","flv":"web"}
        if self.isValid():
            return {"qn": 10000, "format": format,
                    "urls": [self._getRealUrlByPlatform(fmts[format])]}
        return None