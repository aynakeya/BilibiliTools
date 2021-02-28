import glob,json,os

from utils import vwrappers


class ConfigFile:
    proxies = {"http": "http://127.0.0.1:8888"}
    useProxy = False
    downloadProxy = False
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    commonCookies = {}

    saveroute = r"D:\Download\bilidown"
    cookiePath = "cookies"

    aria2rpc = "http://localhost:16800/rpc"
    # if no token provide, using None
    aria2token = None

    defaultDownloader = "aria2"

    # Available: aria2, requests
    useDownloader = {"aria2": True,
                     "requests": True}

    useModules = ["Bilibili", "Info", "MPV", "UniversalDownload",
                  "RealUrl", "M3U8","Search"]

    defaultQuality = 120

    def __init__(self):
        print("Loading config")
        self._loadConfig()
        print("Cookie initialized")
        self.cookies = {}
        self.loadCookie()

    def loadCookie(self):
        for path in glob.glob(os.path.join(os.path.dirname(__file__), self.cookiePath, "*.txt")):
            key = os.path.basename(path)[:-4:]
            with open(path, "r", encoding="utf-8") as f:
                data = f.read().replace(" ", "")
                self.cookies[key] = dict(x.split("=") for x in data.split(";") if x != "")

    def saveCookie(self):
        for key, cookie in self.cookies.items():
            path = os.path.join(os.path.dirname(__file__), self.cookiePath, "{}.txt".format(key))
            with open(path, "w", encoding="utf-8") as f:
                f.write(";".join(map(lambda x: "=".join(x), cookie.items())))

    def getCookie(self, host):
        if host == "":
            return self.commonCookies
        if self.cookies.get(host) == None:
            self.cookies[host] = {}
            return self.cookies[host]
        return self.cookies.get(host)

    @vwrappers.TryExceptRetNone
    def _loadConfig(self,path="config.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            for key,val in data.items():
                if hasattr(self,key):
                    self.__setattr__(key,val)

    def saveConfig(self,path="config.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        with open(path, "w", encoding="utf-8") as f:
            for key,val in data.items():
                if hasattr(self,key):
                    data[key] = self.__getattribute__(key)
            f.write(json.dumps(data,indent=2))


Config = ConfigFile()