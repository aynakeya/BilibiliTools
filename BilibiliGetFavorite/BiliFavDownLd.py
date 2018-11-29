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


def getdata(apiurl,number):

    def tryget(wholeurl):
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
    for pn in range(1,number+1,1):
        print("获取数据: 第%s个==>" % pn,end="")
        #格式化api
        wholeurl = apiurl % pn
        jsondata = tryget(wholeurl)
        code = jsondata["code"]
        if code == 0:
            print("获取成功",end="")
        elif code == 11004:
            print("返回值:11004,返回信息:收藏夹未公开")
            print("请确保收藏夹公开\n程序结束")
            sys.exit()
        else:
            print("返回值:%s,返回信息:%s" % (code, jsondata["message"]))
            while code != 0:
                print("获取数据: 第%s个==>" % pn, end="")
                jsondata = tryget(wholeurl)
                code = jsondata["code"]
            print("获取成功",end="")

        #对于标题，将特殊的Unicode\u 替换成正常字符串.
        data.append({"aid":str(jsondata["data"]["archives"][0]["aid"]),
                     "title":unicdefmt(str(jsondata["data"]["archives"][0]["title"])),
                     "pic":str(jsondata["data"]["archives"][0]["pic"]),
                     "state":str(jsondata["data"]["archives"][0]["state"])})
        print("------(AV号:%s,标题:%s,状态:%s)" % (data[pn-1]["aid"], data[pn-1]["title"],data[pn-1]["state"],))
    return data

def dl(opsys,method,svrt,otptname,url):
    if url == "-1":
        return
    if opsys == "Windows":
        os.system("%s --output-dir \"%s\" --output-filename \"%s\" %s" % (method, svrt, otptname, url))
    else:
        os.system("%s --output-dir %s --output-filename %s %s" % (method, svrt, otptname, url))

def download_by_aria2(data):
    #plz help me
    #i don't know how to do that
    pass

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
            if video["state"] != 0:
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
    if favlink[-1] == "/":
        favlink = favlink[:-1:]
    # 获取mid
    mid = favlink[favlink.find("com/", 0) + 4:favlink.find("/", favlink.find("com/", 0)+4):]
    # 获取fid
    fid = favlink[favlink.find("fid", 0) + 4::]
    if not mid.isdigit():
        mid = ""
    if not fid.isdigit():
        fid = ""
    if len(vmid) == 0 or len(fid) == 0:
        print("Not a Proper Link")
        sys.exit()
    print("You vmid is: %s, you fid is: %s" %(vmid,fid))
    # api链接
    apiurl = apiurl % (vmid, fid, "%s")
    data = getdata(apiurl,number)
    if usemulti:
        download_multi(opsys, data, (datasvrt, imgsvrt, videosvrt), dcv,method = method)
    else:
        download(opsys,data,(datasvrt, imgsvrt, videosvrt), dcv,method = method)
    print("程序结束")
    sys.exit()