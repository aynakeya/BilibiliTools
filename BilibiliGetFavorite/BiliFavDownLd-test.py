from urllib import request
import json,time,os,platform,sys,getopt
from multiprocessing import Pool

rplchrdict_unix = {"/": "-",
             "\\": "-",
             ":": "-",
             "*": "-",
             "?": "-",
             "<": "-",
             ">": "-",
             "|": "-",
             "：" : "-",
             "\"" : "-",
             "→" : "-",
             " " : "' '",
             "&" : "-",
             "'" : "\"'\"",
             "(" : "-",
             ")" : "-"
            }

rplchrdict_windows = {"/": "-",
             "\\": "-",
             ":": "-",
             "*": "-",
             "?": "-",
             "<": "-",
             ">": "-",
             "|": "-",
             "：" : "-",
             "\"" : "-",
             "→" : "-",
             "&" : "-",
            }

unicdchr = {"\\u0026": "&",
              "\\u003c" : "<",
              "\\u003e" : ">"}

apiurl = "https://api.bilibili.com/x/space/fav/arc?vmid=%s&ps=1&fid=%s&pn=%s" % ("%s", "%s", "%s")

def rplchr(s,opsys) :
    if opsys == "Windows":
        chrdict = rplchrdict_windows
    else:
        chrdict = rplchrdict_unix

    newstr = ""
    for i in range(len(s)):
        if s[i] in chrdict:
            newstr += chrdict[s[i]]
        else:
            newstr += s[i]
    if s[0] == "-":
        s = "rmv"+s
    return newstr

def unicdefmt(s):
    for key, value in unicdchr.items():
        s = s.replace(key, value)
    return s

class favfolder(object):
    def __init__(self,media_id,ps = 20,maxnum=1000):
        self.__media_id = media_id
        self.__ps = ps
        self.__maxnum = maxnum
        self.__apiurl = "https://api.bilibili.com/medialist/gateway/base/spaceDetail?media_id=%s&ps=%s&pn=%s" % (self.__media_id, self.__ps, "%s")
        if self.isValid():
            self.__data = self.reqData()
        else:
            self.__data = []

    @classmethod
    def initFromLink(cls,favlink,maxnum=1000):
        parameters = favlink[favlink.find("?", 0) + 1::].split("&")
        media_id = ""
        for para in parameters:
            if "fid" in para:
                media_id = para[4::]
        if not media_id.isdigit():
            media_id = ""
        return cls(media_id,maxnum=maxnum)

    def isValid(self):
        if len(self.__media_id) == 0:
            return False
        else:
            return True

    def isNone(self):
        if len(self.__data) == 0:
            return True
        else:
            return False

    def getNumVideo(self):
        return len(self.__data)


    def getData(self,ps=20):
        parsedlist = [[] for i in range((self.getNumVideo() - 1) // ps + 1)]
        for i in range(self.getNumVideo()):
            parsedlist[i // ps].append(self.__data[i])
        return parsedlist


    def reqData(self):
        def tryget(wholeurl):
            try:
                wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
                jsondata = json.loads(wholeHTML)
            except:
                print("获取失败，暂停3秒")
                print("获取数据: 第%s页==>" % pn, end="")
                time.sleep(3)
                while True:
                    try:
                        wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
                        jsondata = json.loads(wholeHTML)
                        break
                    except:
                        print("获取失败，暂停3秒")
                        print("获取数据: 第%s页==>" % pn, end="")
                        time.sleep(3)
            return jsondata

        data = []
        pn = 1
        n = 0
        while True:
            wholeurl = self.__apiurl % pn

            jsondata = tryget(wholeurl)
            code = jsondata["code"]
            if code != 0:
                return []
            if not "data" in jsondata.keys():
                return []
            else:
                while not "data" in jsondata.keys():
                    jsondata = tryget(wholeurl)

            if jsondata["data"]["info"]["media_count"] == 0:
                break
            medias = jsondata["data"]["medias"]

            print("获取成功")
            for item in medias:
                data.append({"aid": str(item["id"]),
                             "title": unicdefmt(str(item["title"])),
                             "pic": str(item["cover"]),
                             "state": str(item["attr"]),
                             "mid": str(item["upper"]["mid"]),
                             "upname": str(item["upper"]["name"])})
                print("--(AV号:%s,标题:%s,状态:%s)" % (str(item["id"]),unicdefmt(str(item["title"])), str(item["attr"])))
                n += 1
                if n >= self.__maxnum:
                    return data

            pn +=1
        return data

def dl(opsys,method,svrt,otptname,url):
    if url == "-1":
        return
    if opsys == "Windows":
        os.system("%s --output-dir \"%s\" --output-filename \"%s\" %s" % (method, svrt, otptname, url))
    else:
        os.system("%s --output-dir %s --output-filename %s %s" % (method, svrt, otptname, url))

def download(opsys,data, route, dcv, method = "you-get"):

    videourl = "https://www.bilibili.com/video/av"
    datasvrt,imgsvrt,videosvrt = route
    if dcv[0]:
        with open(datasvrt, "w", encoding="utf-8") as exfile:
            for video in data:
                exfile.write((video["aid"] + "---" + video["title"] + "---" + video["pic"] + "\n"))
        print("Finish export data")
    else:
        print("Skip export data")

    if dcv[1]:
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"],opsys)
            dl(opsys, method, imgsvrt, otptname, video["pic"])
        print("Finish download covers")
    else:
        print("Skip download covers")

    if dcv[2]:
        for video in data:
            if video["state"] != "0":
                print("视频失效或其他原因")
                continue
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"], opsys)
            dl(opsys, method, videosvrt, otptname, videourl + video["aid"])
        print("Finish download video")
    else:
        print("Skip download videos")

    return "finish"


def download_multi(opsys, data, route, dcv, method = "you-get"):

    videourl = "https://www.bilibili.com/video/av"
    datasvrt,imgsvrt,videosvrt = route
    if dcv[0]:
        with open(datasvrt, "w", encoding="utf-8") as exfile:
            for video in data:
                exfile.write((video["aid"] + "---" + video["title"] + "---" + video["pic"] + "\n"))
        print("Finish export data")
    else:
        print("Skip export data")

    if dcv[1]:
        p = Pool()
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"], opsys)
            p.apply_async(dl, (opsys, method, imgsvrt, otptname, video["pic"]))
        p.close()
        p.join()
        print("Finish download covers")
    else:
        print("Skip download covers")

    if dcv[2]:
        p = Pool()
        for video in data:
            if video["state"] != "0":
                print("下载视频:%s(aid:%s)时出现问题，视频失效或其他原因" % (video["title"],video["aid"]))
                continue
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"], opsys)
            p.apply_async(dl, (opsys, method, videosvrt, otptname, videourl+video["aid"]))
        p.close()
        p.join()
        print("Finish download video")
    else:
        print("Skip download videos")
    return "finish"

if __name__ == "__main__":
    # 获取操作系统类型
    opsys = platform.system()
    svrt = sys.path[0]
    datasvrt = os.path.join(svrt,"data.txt")
    imgsvrt = os.path.join(svrt,"img")
    videosvrt = os.path.join(svrt,"video")
    number = 1
    method = "you-get"
    dcv = [False,False,False]
    usemulti = False
    try:
        options, args = getopt.getopt(sys.argv[1:], "hdcvms:n:", ["help", "saveroute=", "number=","method="])
    except:
        print("illegal option")
        sys.exit()
    for key,value in options:
        if key == "-h" or key == "--help":
            print("python BiliFavDownLD.py "
                  "[-s] [-n] [-d] [-c] [-v] [-m] [--method] favlink")
            print("Options:\n"
                  "-s/--saveroute: saveroute(default: current dir)\n"
                  "-n/--number: number u want to download(default: 1)\n"
                  "-d: export data\n"
                  "-c: download cover\n"
                  "-v: download video\n"
                  "-m: use muliprocessing\n"
                  "--method: use which to download(default:you-get)")
            print("程序结束")
            sys.exit()
        if key == "-d":
            dcv[0] = True
        if key == "-c":
            dcv[1] = True
        if key == "-v":
            dcv[2] = True
        if key == "-m":
            usemulti = True
        if key == "--method":
            method = str(value)
        if key == "-s" or key == "--saveroute":
            if not os.path.exists(str(value)):
                print("Path not exist")
                sys.exit()
            else:
                svrt = str(value)
                datasvrt = os.path.join(svrt, "data.txt")
                imgsvrt = os.path.join(svrt, "img")
                videosvrt = os.path.join(svrt, "video")
        if key == "-n" or key == "--number":
            if str(value).isdigit():
                number = int(value)
            else:
                print("Not a correct number")
                sys.exit()
    if len(args) != 1:
        print("No Favorite Link or to much args")
        sys.exit()
    favlink = args[0]
    fav = favfolder.initFromLink(favlink,maxnum=number)
    if not fav.isValid():
        print("Not a Proper Link")
        sys.exit()
    if fav.isNone():
        print("没有获取到数据")
    if usemulti:
        download_multi(opsys, fav.getData(ps=1000)[0], (datasvrt, imgsvrt, videosvrt), dcv,method = method)
    else:
        download(opsys,fav.getData(ps=1000)[0],(datasvrt, imgsvrt, videosvrt), dcv,method = method)
    print("程序结束")
    sys.exit()