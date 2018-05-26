from urllib import request
import json,time,os,platform
from multiprocessing import Pool
from VocaloidParse import parsetitle

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
             "&" : "-"
            }

unicdchr = {"\\u0026": "&",
              "\\u003c" : "<",
              "\\u003e" : ">"}

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


def getdata(number):

    def tryget():
        try:
            wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
            jsondata = json.loads(wholeHTML)
        except:
            print("获取失败，暂停3秒")
            print("获取数据: 第%s个==>" % pn, end="")
            time.sleep(3)
            while True:
                try:
                    wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
                    jsondata = json.loads(wholeHTML)
                    break
                except:
                    print("获取失败，暂停3秒")
                    print("获取数据: 第%s个==>" % pn, end="")
                    time.sleep(3)
        return jsondata

    data = []
    for pn in range(number):
        pn += 1
        print("获取数据: 第%s个==>" % pn,end="")
        #格式化api
        wholeurl = apiurl % pn
        jsondata = tryget()
        code = jsondata["code"]
        if code == 0:
            print("获取成功",end="")
        else:
            print("返回值:%s,返回信息:%s" % (code, jsondata["message"]))
            while code != 0:
                print("获取数据: 第%s个==>" % pn, end="")
                jsondata = tryget()
                code = jsondata["code"]
            print("获取成功",end="")

        #对于标题，将特殊的Unicode\u 替换成正常字符串.
        data.append({"aid":str(jsondata["data"]["archives"][0]["aid"]),
                     "title":unicdefmt(str(jsondata["data"]["archives"][0]["title"])),
                     "pic":str(jsondata["data"]["archives"][0]["pic"])})
        print("------(AV号:%s,标题:%s)" % (data[pn-1]["aid"], data[pn-1]["title"]))
    return data

def dl(opsys,method,svrt,otptname,url):
    if opsys == "Windows":
        os.system("%s --output-dir \"%s\" --output-filename \"%s\" %s" % (method, svrt, otptname, url))
    else:
        os.system("%s --output-dir %s --output-filename %s %s" % (method, svrt, otptname, url))

def download_by_aria2(data):
    #plz help me
    #i don't know how to do that
    pass

def download(data, route, method = "you-get"):

    videourl = "https://www.bilibili.com/video/av"
    datasvrt,imgsvrt,videosvrt = route
    expt = input("Export Data? y/n ")
    if expt == "y":
        with open(datasvrt, "w", encoding="utf-8") as exfile:
            for video in data:
                exfile.write((video["aid"] + "---" + video["title"] + "---" + video["pic"] + "\n"))
        print("Finish export data")
    else:
        print("Skip")

    downldpic = input("Download Covers? y/n ")
    if downldpic == "y":
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"],opsys)
            dl(opsys, method, imgsvrt, otptname, video["pic"])
        print("Finish download covers")
    else:
        print("Skip")

    downld = input("Download Video? y/n ")
    if downld == "y":
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"], opsys)
            dl(opsys, method, videosvrt, otptname, videourl + video["aid"])
        print("Finish download video")
    else:
        print("Skip")

    return "finish"


def download_multi(data, route, opsys, method = "you-get"):

    videourl = "https://www.bilibili.com/video/av"
    datasvrt,imgsvrt,videosvrt = route
    expt = input("Export Data? y/n ")
    if expt == "y":
        with open(datasvrt, "w", encoding="utf-8") as exfile:
            for video in data:
                exfile.write((video["aid"] + "---" + video["title"] + "---" + video["pic"] + "\n"))
        print("Finish export data")
    else:
        print("Skip")

    downldpic = input("Download Covers? y/n ")
    if downldpic == "y":
        p = Pool()
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = rplchr(video["title"], opsys)
            p.apply_async(dl, (opsys, method, imgsvrt, otptname, video["pic"]))
        p.close()
        p.join()
        print("Finish download covers")
    else:
        print("Skip")

    downld = input("Download Video? y/n ")
    if downld == "y":
        p = Pool()
        for video in data:
            # 使用代替特殊字符后的标题
            otptname = parsetitle(rplchr(video["title"], opsys))
            p.apply_async(dl, (opsys, method, videosvrt, otptname, videourl+video["aid"]))
        p.close()
        p.join()
        print("Finish download video")
    else:
        print("Skip")
    return "finish"

if __name__=="__main__":
    #获取操作系统类型
    opsys = platform.system()
    favlink = input("Enter Favorite Folder Link")
    #如果最后有/则去掉/
    if favlink[-1] == "/":
        favlink = favlink[:-1:]
    #获取vmid
    vmid = favlink[favlink.find("com", 0) + 4:favlink.find("/#", 0):]
    #获取fid
    fid = favlink[favlink.find("fid", 0) + 4::]
    #api链接
    apiurl = "https://api.bilibili.com/x/v2/fav/video?vmid=%s&ps=1&fid=%s&pn=%s" % (vmid, fid, "%s")
    #获取需要个数
    number = int(input("enter your number: "))
    datasvrt = input("Enter data save route(full)")
    imgsvrt = input("Enter image save route(full)")
    videosvrt = input("Enter video save route(full)")

    data = getdata(number)
    download_multi(data,(datasvrt,imgsvrt,videosvrt))