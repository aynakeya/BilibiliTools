from urllib import request
import json, time, os, platform, sys, getopt, requests,re
from multiprocessing import Pool
from pyaria2 import Aria2RPC

def filenameparser(filename):
    pattern = r'[\\/:*?"<>|\r\n]+'
    return re.sub(pattern,"-",filename)

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

def httpConnect(url, maxReconn=5, **kwargs):
    trial = 0
    while trial < maxReconn:
        try:
            return requests.get(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None

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
        self.getPages()
        self.getInfo()

    @classmethod
    def initFromUrl(cls,url):
        pattern = r"av[0-9]*"
        return cls(re.search(pattern,url).group()[2::])

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

    def downloadByYouGet(self):
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

class favfolder():
    def __init__(self,fid):
        self.fid = fid
        self.videos = []

    def getVideos(self,num=1000):

v = biliVideo(66851210)
# v = biliVideo.initFromUrl("https://www.bilibili.com/video/av53020609")
v.downloadBySimple()
v.downloadByAria(qn=116)

# if __name__ == "__main__":
#     # 获取操作系统类型
#     opsys = platform.system()
#     svrt = sys.path[0]
#     datasvrt = os.path.join(svrt, "data.txt")
#     imgsvrt = os.path.join(svrt, "img")
#     videosvrt = os.path.join(svrt, "video")
#     number = 1
#     method = "you-get"
#     dcv = [False, False, False]
#     usemulti = False
#     try:
#         options, args = getopt.getopt(sys.argv[1:], "hdcvms:n:", ["help", "saveroute=", "number=", "method="])
#     except:
#         print("illegal option")
#         sys.exit()
#     for key, value in options:
#         if key == "-h" or key == "--help":
#             print("python BiliFavDownLD.py "
#                   "[-s] [-n] [-d] [-c] [-v] [-m] [--method] favlink")
#             print("Options:\n"
#                   "-s/--saveroute: saveroute(default: current dir)\n"
#                   "-n/--number: number u want to download(default: 1)\n"
#                   "-d: export data\n"
#                   "-c: download cover\n"
#                   "-v: download video\n"
#                   "-m: use muliprocessing\n"
#                   "--method: use which to download(default:you-get)")
#             print("程序结束")
#             sys.exit()
#         if key == "-d":
#             dcv[0] = True
#         if key == "-c":
#             dcv[1] = True
#         if key == "-v":
#             dcv[2] = True
#         if key == "-m":
#             usemulti = True
#         if key == "--method":
#             method = str(value)
#         if key == "-s" or key == "--saveroute":
#             if not os.path.exists(str(value)):
#                 print("Path not exist")
#                 sys.exit()
#             else:
#                 svrt = str(value)
#                 datasvrt = os.path.join(svrt, "data.txt")
#                 imgsvrt = os.path.join(svrt, "img")
#                 videosvrt = os.path.join(svrt, "video")
#         if key == "-n" or key == "--number":
#             if str(value).isdigit():
#                 number = int(value)
#             else:
#                 print("Not a correct number")
#                 sys.exit()
#     if len(args) != 1:
#         print("No Favorite Link or to much args")
#         sys.exit()
#     favlink = args[0]
#     if favlink[-1] == "/":
#         favlink = favlink[:-1:]
#     # 获取mid
#     mid = favlink[favlink.find("com/", 0) + 4:favlink.find("/", favlink.find("com/", 0) + 4):]
#     # 获取fid
#     fid = favlink[favlink.find("fid", 0) + 4::]
#     if not mid.isdigit():
#         mid = ""
#     if not fid.isdigit():
#         fid = ""
#     if len(mid) == 0 or len(fid) == 0:
#         print("Not a Proper Link")
#         sys.exit()
#     print("You vmid is: %s, you fid is: %s" % (mid, fid))
#     # api链接
#     apiurl = apiurl % (mid, fid, "%s")
#     data = getdata(apiurl, number)
#     if usemulti:
#         download_multi(opsys, data, (datasvrt, imgsvrt, videosvrt), dcv, method=method)
#     else:
#         download(opsys, data, (datasvrt, imgsvrt, videosvrt), dcv, method=method)
#     print("程序结束")
#     sys.exit()
