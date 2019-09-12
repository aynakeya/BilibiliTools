from pyaria2 import Aria2RPC
import os, re
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
    saveroute = r"E:\Download"

    aria2rpc = "http://localhost:6800/rpc"
    #if no token provide, using None
    aria2token = None

class ariaDownloader():
    def __init__(self, url=Config.aria2rpc, token=Config.aria2token):
        self.rpc = Aria2RPC(url=url, token=token)

    def download(self, url, route, filename, **kwargs):
        kwargs["dir"] = route
        kwargs["out"] = filenameparser(filename)
        self.rpc.addUri([url], kwargs)

class simpleDownloader():
    def __init__(self):
        pass

    def download(self, url, route, fn,**kwargs):
        fn = filenameparser(fn)
        raw_data = httpConnect(url,**kwargs)
        if raw_data == None:
            return False
        path = os.path.join(route, fn)
        if not os.path.exists(route):
            os.mkdir(route)
        with open(path,"wb+") as f:
            f.write(raw_data.content)
        return True

class yougetDownloader():
    def __init__(self):
        pass

    def download(self, url, route, filename):
        os.system("you-get --output-dir \"%s\" --output-filename \"%s\" %s" % (route, filenameparser(filename), url))

aria = ariaDownloader()
youget = yougetDownloader()
simpled = simpleDownloader()

class biliVideo():
    videoUrl = "https://www.bilibili.com/video/av%s"
    pagesApi = "https://www.bilibili.com/widget/getPageList?aid=%s"
    detailApi = "https://api.bilibili.com/x/web-interface/view/detail?aid=%s&jsonp=jsonp"
    playurlApi = "https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=%s&type=&otype=json"

    def __init__(self,aid):
        self.aid = aid
        self.pages = []
        self.title = ""
        self.uploader = ""

    @classmethod
    def initFromAid(cls,aid):
        v = cls(aid)
        v.getPages()
        v.getInfo()
        return v

    @classmethod
    def initFromUrl(cls,url):
        pattern = r"av[0-9]*"
        return cls(re.search(pattern,url).group()[2::])

    @classmethod
    def initFromData(cls, aid, title, uploader, pages):
        v = cls(aid)
        v.title = title
        v.uploader = uploader
        v.pages = pages
        return v

    def getPages(self):
        data = httpConnect(self.pagesApi % self.aid)
        if data == None:
            return
        self.pages = data.json()

    def getInfo(self):
        data = httpConnect(self.detailApi % self.aid)
        if data == None:
            return
        data = data.json()
        self.title = data["data"]["View"]["title"]
        self.uploader = data["data"]["View"]["owner"]["name"]

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


    def downloadByAria(self,page=1,qn=116):
        data = self.getPlayurl(page=page,qn=qn)
        if len(data["urls"]) == 0:
            return
        url = data["urls"][0]
        suffix = url.split("?")[0].split(".")[-1]
        aria.download(url,Config.saveroute,".".join([self.title+" - "+self.uploader,suffix]),
                      header=["origin: www.bilibili.com","referer:"+self.videoUrl%self.aid,
                              "user-agent:%s"%Config.commonHeaders["user-agent"]])

    def downloadByYouGet(self,**kwargs):
        youget.download(self.videoUrl%self.aid,Config.saveroute,self.title)

    def downloadBySimple(self,page=1,qn=116):
        data = self.getPlayurl(page=page, qn=qn)
        if len(data["urls"]) == 0:
            return
        url = data["urls"][0]
        suffix = url.split("?")[0].split(".")[-1]
        simpled.download(url,Config.saveroute,".".join([self.title+" - "+self.uploader,suffix]),
                         headers={"origin": "www.bilibili.com","referer":self.videoUrl%self.aid,
                                  "user-agent":Config.commonHeaders["user-agent"]})

    def downloadSelector(self,method):
        selectors = {"youget": self.downloadByYouGet,
                             "you-get": self.downloadByYouGet,
                             "simple": self.downloadBySimple,
                             "aria": self.downloadByAria}
        if method in selectors:
            return selectors[method]
        return None

class favfolder():
    favApi = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?ps=20&jsonp=jsonp&media_id=%s&pn=%s"
    def __init__(self,media_id):
        self.media_id = media_id
        self.videos = []

    def getVideos(self,maxNum=1000):
        self.clearData()
        pn = 1
        num = 0
        data = httpConnect(self.favApi%(self.media_id,pn),headers=Config.commonHeaders)
        if data == None:
            return
        data = data.json()
        for media in data["data"]["medias"]:
            if num >= maxNum:
                break
            aid = media["id"]
            title = media["title"]
            uploader = media["upper"]["name"]
            pages = [{"page":p["page"],"pagename":p["title"],"cid":p["id"]} for p in media["pages"]]
            self.videos.append(biliVideo.initFromData(aid,title,uploader,pages))
            num +=1
        return

    def clearData(self):
        self.videos.clear()

    def downloadAll(self,method,**kwargs):
        video: biliVideo
        for video in self.videos:
            df = video.downloadSelector(method)
            if df == None:
                return
            df(**kwargs)

# v = biliVideo(66851210)
# v = biliVideo.initFromUrl("https://www.bilibili.com/video/av53020609")
# v.downloadBySimple()
# v.downloadByAria(qn=116)
#
# f = favfolder(278832132)
# f.getVideos(10)
# for v in f.videos:
#     print(v.aid,v.title,v.pages)
# f.downloadAll("aria")
