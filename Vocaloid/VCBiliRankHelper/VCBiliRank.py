import requests,re
import json,time,sys,os
from functools import reduce


class vsingersparser(object):
    def __init__(self):
        self.__vsingerlist = ["洛天依", "言和", "乐正绫", "心华", "星尘", "乐正龙牙", "初音未来", "墨清弦", "徵羽摩柯"]
        self.__vsingerdict = {"洛天依": 2,  # 0b10
                       "乐正绫": 4,  # 0b100
                       "言和": 8,  # 0b1000
                       "心华": 16,  # 0b10000
                       "星尘": 32,  # 0b100000
                       "乐正龙牙": 64,  # 0b1000000
                       "龙牙": 64,
                       "初音未来": 128,
                       "初音": 128,
                       "墨清弦": 256,
                       "徵羽摩柯": 512,
                       "摩柯": 512,
                       }
        self.__vsingersdict = {"0": ""}
        self.combinesingers([], self.__vsingerlist)

    def getkey(self,singerlist):
        return str(reduce(lambda x, y: x + y, map(lambda singer: self.__vsingerdict[singer], singerlist)))

    def combinesingers(self,used,notused):
        if len(notused) < 1:
            return
        newnotused = notused.copy()
        for singer in notused:
            newused = used.copy()
            newused.append(singer)
            newnotused.remove(singer)
            self.__vsingersdict[self.getkey(newused)] = newused
            self.combinesingers(newused, newnotused)

    def getSingersByTitleParser(self,title):
        singerskey = 0
        if title == None:
            title = ""
        for singer in self.__vsingerdict:
            if singer in title:
                if singerskey & (1 << (str(bin(self.__vsingerdict[singer])).count('0') - 1)):
                    continue
                singerskey += self.__vsingerdict[singer]

        if singerskey == 0:
            return []
        else:
            return self.__vsingersdict[str(singerskey)]

    def getParsedTitle(self,title):
        if title == None:
            title = ""
        titlebackup = title
        if title.find("】") >= 0:
            title = title[title.find("】") + 1::]
        if title.find("【") >= 0:
            title = title[:title.find("【"):]

        if len(title) > 0:
            return title
        else:
            return titlebackup

class rankitem(object):
    def __init__(self,aid,title,parsedtitle,singers,author):
        self.__title = title
        self.__aid = aid
        self.__parsedtitle = parsedtitle
        self.__singers = singers
        self.__author = author

    @classmethod
    def initFromitem(cls,item,parser,method=0):
        title = item["title"]
        aid = item["avid"]
        parsedtitle = parser.getParsedTitle(title)
        if method == 0:
            singers = parser.getSingersByTitleParser(title)
        else:
            singers = []
        return cls(aid,title,parsedtitle,singers,cls.reqUp(aid))

    @classmethod
    def initFromAid(cls, aid, parser, method=0):
        title,author = cls.reqInfo(aid)
        parsedtitle = parser.getParsedTitle(title)
        if method == 0:
            singers = parser.getSingersByTitleParser(title)
        else:
            singers = []
        return cls(aid, title, parsedtitle, singers, author)

    @classmethod
    def reqInfo(cls,aid):
        url = "https://api.bilibili.com/x/web-interface/search/all?keyword=av%s" % aid
        wb_data = requests.get(url)
        data = json.loads(wb_data.text)
        if len(data["data"]["result"]["video"]) == 0:
            return (None,None)
        else:
            rs = data["data"]["result"]["video"][0]
            return (rs["title"],rs["author"])

    @classmethod
    def reqUp(self,aid):
        url = "https://api.bilibili.com/x/web-interface/search/all?keyword=av%s" % aid
        wb_data = requests.get(url)
        data = json.loads(wb_data.text)
        if len(data["data"]["result"]["video"]) == 0:
            return None
        else:
            rs = data["data"]["result"]["video"][0]
            return rs["author"]

    def getTitle(self):
        return self.__title

    def getAid(self):
        return self.__aid

    def getParsedTitle(self):
        return self.__parsedtitle

    def getSingers(self):
        return self.__singers

    def getAuthor(self):
        return self.__author

#以下为主榜更新后的方法
def rank_a():
    # 主榜1-20
    print("从官网获取主榜1-20名数据")
    url = "http://vc.biliran.moe/"
    wb_data = requests.get(url)
    ranlist = re.search(r"list:\[([\s\S]*)\]", wb_data.text)
    ranlist = json.loads(str(ranlist.group()[5:]))
    mainranklist = []
    for item in ranlist:
        mainranklist.append(rankitem.initFromitem(item, parser))
    print("获取成功")
    print("------------------------------------")

    print("手动输入剩余数据")

    # op
    opaid = input("输入op: ")
    op = rankitem.initFromAid(opaid, parser)
    print("获取op信息成功")
    print("------------------------------------")

    # superhit
    i = 1
    superhitlist = []
    aid = input("请输入SuperHit曲目%s: " % i)
    while aid != ".":
        i += 1
        superhitlist.append(rankitem.initFromAid(aid, parser))
        aid = input("请输入SuperHit曲目%s: " % i)
    print("获取SuperHit信息成功")
    print("------------------------------------")

    # 主榜21-30
    submainranklist = []
    for i in range(10):
        aid = input("输入第%s名: " % (30 - i))
        submainranklist.append(rankitem.initFromAid(aid, parser))
    submainranklist.reverse()
    mainranklist.extend(submainranklist)
    print("获取21-30信息成功")
    print("------------------------------------")

    # 新曲推荐
    i = 1
    pickuplist = []
    aid = input("请输入新曲推荐曲目%s: " % i)
    while aid != ".":
        i += 1
        pickuplist.append(rankitem.initFromAid(aid, parser))
        aid = input("请输入新曲推荐曲目%s: " % i)
    print("获取新曲推荐信息成功")
    print("------------------------------------")

    # woc一年了
    woclist = []
    for i in range(5):
        aid = input("输入woc第%s名: " % (5 - i))
        woclist.append(rankitem.initFromAid(aid, parser))
    print("获取woc一年了榜单信息成功")
    print("------------------------------------")

    print("输出:\n\n\n")

    print("op %s %s %s av%s" % (op.getParsedTitle(), op.getSingers(),
                                op.getAuthor(), op.getAid()))
    print("\n\n\n主榜")

    for i in range(30):
        print("主榜%s %s %s %s av%s" % (30 - i, mainranklist[29 - i].getParsedTitle(), mainranklist[29 - i].getSingers(),
                                      mainranklist[29 - i].getAuthor(), mainranklist[29 - i].getAid()))
    print("\n\n\n新曲推荐")

    for i in range(len(pickuplist)):
        print("新曲推荐%s %s %s %s av%s" % (i + 1, pickuplist[i].getParsedTitle(), pickuplist[i].getSingers(),
                                        pickuplist[i].getAuthor(), pickuplist[i].getAid()))
    print("\n\n\nwoc一年了")

    for i in range(5):
        print("woc%s %s %s %s av%s" % (5 - i, woclist[i].getParsedTitle(), woclist[i].getSingers(),
                                       woclist[i].getAuthor(), woclist[i].getAid()))
    print("\n\n\n")

# 纯手抄
def rank_b():
    print("手动输入剩余数据")
    print("输入\".\"代表结束")
    print("输入\"/\"代表重新输入")

    # op
    opaid = input("输入op: ")
    if opaid[len(opaid)-1] != ".":
        while opaid[len(opaid) - 1] == "/":
            opaid = input("输入op: ")
        op = rankitem.initFromAid(opaid, parser)
        print("获取op信息成功")
    else:
        print("放弃输入op信息")
        op = rankitem.initFromAid("837grewyf8ubhd28q", parser)
    print("------------------------------------")

    # superhit
    i = 1
    superhitlist = []

    while True:
        aid = input("请输入SuperHit曲目%s: " % i)

        if aid[len(aid)-1] == ".":
            print("放弃输入")
            break

        if aid[len(aid)-1] == "/":
            if i > 1:
                i -= 1
                superhitlist.pop()
            continue

        i += 1
        superhitlist.append(rankitem.initFromAid(aid, parser))


    print("获取SuperHit信息成功 歌曲数: %s " % (i-1))
    print("------------------------------------")


    # 主榜11-30
    i = 30
    mainranklist = []

    while i > 10:
        aid = input("请输入主榜第%s名: " % i)
        if aid[len(aid)-1] == ".":
            print("放弃输入")
            break
        if aid[len(aid)-1] == "/":
            if i < 30 :
                i += 1
                mainranklist.pop()
            continue
        mainranklist.append(rankitem.initFromAid(aid, parser))
        i -= 1

    print("获取主榜11-30信息成功")
    print("------------------------------------")

    # 新曲推荐
    i = 1
    pickuplist = []

    while True:
        aid = input("请输入新曲推荐曲目%s: " % i)

        if aid[len(aid)-1] == ".":
            print("放弃输入")
            break

        if aid[len(aid)-1] == "/":
            if i > 1:
                i -= 1
                pickuplist.pop()
            continue
        i += 1
        pickuplist.append(rankitem.initFromAid(aid, parser))


    print("获取新曲推荐信息成功 --歌曲数: %s" % (i-1))
    print("------------------------------------")

    # 主榜4-10
    i = 10

    while i > 3:
        aid = input("请输入主榜第%s名: " % i)
        if aid[len(aid)-1] == ".":
            print("放弃输入")
            break
        if aid[len(aid)-1] == "/":
            if i < 10 :
                i += 1
                mainranklist.pop()
            continue
        mainranklist.append(rankitem.initFromAid(aid, parser))
        i -= 1

    print("获取主榜4-10信息成功")
    print("------------------------------------")

    # woc一年了
    i = 5
    woclist = []


    while i > 0:
        aid = input("请输入woc榜第%s名: " % i)
        if aid[len(aid)-1] == ".":
            print("放弃输入")
            break
        if aid[len(aid)-1] == "/":
            if i < 5 :
                i += 1
                woclist.pop()
            continue
        woclist.append(rankitem.initFromAid(aid, parser))
        i -= 1

    print("获取woc一年了榜单信息成功")
    print("------------------------------------")

    # 主榜1-3
    i = 3

    while i > 0:
        aid = input("请输入主榜第%s名: " % i)
        if aid[len(aid) - 1] == ".":
            print("放弃输入")
            break
        if aid[len(aid) - 1] == "/":
            if i < 3 :
                i += 1
                mainranklist.pop()
            continue
        mainranklist.append(rankitem.initFromAid(aid, parser))
        i -= 1

    print("获取主榜1-3信息成功")
    print("------------------------------------")

    counts = getsingercount(op, mainranklist, superhitlist, pickuplist, woclist)
    output(op, mainranklist, superhitlist, pickuplist, woclist, counts)
    return (op, mainranklist, superhitlist, pickuplist, woclist)

# 使用文件导入数据
def rank_c(filedir,parser):
    mainranklist, pickuplist, woclist, superhitlist = [],[],[],[]
    op = rankitem.initFromAid("54ytrhg2qawe5yes", parser)
    with open(filedir,"r",encoding="utf-8") as f:
        for line in f.readlines():
            l = line.strip().split("=")
            if ((l[0].split("_")[0]) == "zb") and (len(l[1]) != 0):
                mainranklist.append(rankitem.initFromAid(l[1], parser))
            elif (l[0].split("_")[0] == "woc") and (len(l[1]) != 0):
                woclist.append(rankitem.initFromAid(l[1], parser))
            elif (l[0] == "pickup") and (len(l[1]) != 0):
                pickuplist.append(rankitem.initFromAid(l[1], parser))
            elif (l[0] == "superhit") and (len(l[1]) != 0):
                superhitlist.append(rankitem.initFromAid(l[1], parser))
            elif (l[0] == "op") and (len(l[1]) != 0):
                op = rankitem.initFromAid(l[1], parser)
            else:
                pass
            time.sleep(0.1)
    counts = getsingercount(op, mainranklist, superhitlist, pickuplist, woclist)
    output(op, mainranklist, superhitlist, pickuplist, woclist, counts)
    return (op, mainranklist, superhitlist, pickuplist, woclist,counts)

def output(op,mainranklist, superhitlist, pickuplist,woclist,counts,filedir = ""):
    print("输出:\n\n\n")

    print("op:【%s】 %s  %s av%s" % (",".join(op.getSingers()), op.getParsedTitle(),
                                  op.getAuthor(), op.getAid()))


    for i in range(30):
        print(
            "主榜%s:【%s】 %s （UP:%s） av%s" % (30 - i, ",".join(mainranklist[i].getSingers()), mainranklist[i].getParsedTitle(),
                                       mainranklist[i].getAuthor(), mainranklist[i].getAid()))
    for key, value in counts["mainranklist"].items():
        if value > 0:
            print("【%s】: %s" % (key, value), end=" ")

    print("\n\n\nSuperHits")


    for i in range(len(superhitlist)):
        print("SuperHits%s 【%s】 %s （UP:%s） av%s" % (
        i + 1, ",".join(superhitlist[i].getSingers()), superhitlist[i].getParsedTitle(),
        superhitlist[i].getAuthor(), superhitlist[i].getAid()))

    for key, value in counts["superhitlist"].items():
        if value > 0:
            print("【%s】: %s" % (key, value), end=" ")

    print("\n\n\n新曲推荐")

    for i in range(len(pickuplist)):
        print("新曲推荐%s 【%s】 %s （UP:%s） av%s" % (i + 1, ",".join(pickuplist[i].getSingers()), pickuplist[i].getParsedTitle(),
                                          pickuplist[i].getAuthor(), pickuplist[i].getAid()))

    for key, value in counts["pickuplist"].items():
        if value > 0:
            print("【%s】: %s" % (key, value), end=" ")



    print("\n\n\nwoc一年了")

    for i in range(5):
        print("woc%s 【%s】 %s （UP:%s） av%s" % (5 - i, ",".join(woclist[i].getSingers()), woclist[i].getParsedTitle(),
                                         woclist[i].getAuthor(), woclist[i].getAid()))
    for key, value in counts["woclist"].items():
        if value > 0:
            print("【%s】: %s" % (key, value), end=" ")

    print("\n\n\n")


def generateinputtxt():
    with open("input.txt", "w", encoding="utf-8") as exfile:
        exfile.write("---------------------------------------------------------\n")
        exfile.write("***使用指南***\n")
        exfile.write("*在=后面输入av号(不带av) 如：28922961\n")
        exfile.write("*op:片头曲，zb:主榜，superhit:superhit，woc:woc一年了, pickup:新曲推荐\n")
        exfile.write("*如果有多个pickup或superhit, 复制 如pickup= 到下一行 在填入即可\n")
        exfile.write("*如果没有请留空或删除\n")
        exfile.write("---------------------------------------------------------\n")
        exfile.write("op=\n")
        exfile.write("---------------------------------------------------------\n")
        for i in range(30, 0, -1):
            exfile.write("zb_%s=\n" % i)
        exfile.write("---------------------------------------------------------\n")
        for i in range(5, 0, -1):
            exfile.write("woc_%s=\n" % i)
        exfile.write("---------------------------------------------------------\n")
        exfile.write("pickup=\n")
        exfile.write("---------------------------------------------------------\n")
        exfile.write("superhit=\n")

def txtoutput(data):
    op, mainranklist, superhitlist, pickuplist, woclist, counts = data

    with open("output.txt","w",encoding="utf-8") as exfile:
        exfile.write("抄榜结果:\n")
        exfile.write("---------------------------------------------------------\n")


        exfile.write("op:【%s】 %s  %s av%s\n" % (",".join(op.getSingers()), op.getParsedTitle(),
                                       op.getAuthor(), op.getAid()))
        exfile.write("\n---------------------------------------------------------\n")

        exfile.write("主榜\n")
        for i in range(30):
            exfile.write(
                "主榜%s:【%s】 %s （UP:%s） av%s\n" % (
                    30 - i, ",".join(mainranklist[i].getSingers()), mainranklist[i].getParsedTitle(),
                    mainranklist[i].getAuthor(), mainranklist[i].getAid()))
        exfile.write("\n")
        for key, value in counts["mainranklist"].items():
            if value > 0:
                exfile.write("【%s】: %s " % (key, value))
        exfile.write("\n---------------------------------------------------------\n")

        exfile.write("SuperHits")
        for i in range(len(superhitlist)):
            exfile.write("SuperHits%s 【%s】 %s （UP:%s） av%s\n" % (
                i + 1, ",".join(superhitlist[i].getSingers()), superhitlist[i].getParsedTitle(),
                superhitlist[i].getAuthor(), superhitlist[i].getAid()))
        exfile.write("\n")
        for key, value in counts["superhitlist"].items():
            if value > 0:
                exfile.write("【%s】: %s " % (key, value))
        exfile.write("\n---------------------------------------------------------\n")

        exfile.write("新曲推荐\n")
        for i in range(len(pickuplist)):
            exfile.write("新曲推荐%s 【%s】 %s （UP:%s） av%s\n" % (
                i + 1, ",".join(pickuplist[i].getSingers()), pickuplist[i].getParsedTitle(),
                pickuplist[i].getAuthor(), pickuplist[i].getAid()))
        exfile.write("\n")
        for key, value in counts["pickuplist"].items():
            if value > 0:
                exfile.write("【%s】: %s " % (key, value))
        exfile.write("\n---------------------------------------------------------\n")

        exfile.write("woc一年了\n")
        for i in range(5):
            exfile.write("woc%s 【%s】 %s （UP:%s） av%s\n" % (5 - i, ",".join(woclist[i].getSingers()), woclist[i].getParsedTitle(),
                                                  woclist[i].getAuthor(), woclist[i].getAid()))
        exfile.write("\n")
        for key, value in counts["woclist"].items():
            if value > 0:
                exfile.write("【%s】: %s " % (key, value))
        exfile.write("\n---------------------------------------------------------\n")


def getsingercount(op, mainranklist, superhitlist, pickuplist, woclist):
    counts = {"mainranklist":"","superhitlist":"","pickuplist":"","woclist":""}

    singercount = {"洛天依": 0,  # 0b10
                   "乐正绫": 0,  # 0b100
                   "言和": 0,  # 0b1000
                   "心华": 0,  # 0b10000
                   "星尘": 0,  # 0b100000
                   "乐正龙牙": 0,  # 0b1000000
                   "初音未来": 0,
                   "墨清弦": 0,
                   "徵羽摩柯": 0
                   }
    for i in range(len(mainranklist)):
        for j in mainranklist[i].getSingers():
            singercount[j] += 1
    counts["mainranklist"] = singercount

    singercount = {"洛天依": 0,  # 0b10
                   "乐正绫": 0,  # 0b100
                   "言和": 0,  # 0b1000
                   "心华": 0,  # 0b10000
                   "星尘": 0,  # 0b100000
                   "乐正龙牙": 0,  # 0b1000000
                   "初音未来": 0,
                   "墨清弦": 0,
                   "徵羽摩柯": 0
                   }
    for i in range(len(superhitlist)):
        for j in superhitlist[i].getSingers():
            singercount[j] += 1
    counts["superhitlist"] = singercount

    singercount = {"洛天依": 0,  # 0b10
                   "乐正绫": 0,  # 0b100
                   "言和": 0,  # 0b1000
                   "心华": 0,  # 0b10000
                   "星尘": 0,  # 0b100000
                   "乐正龙牙": 0,  # 0b1000000
                   "初音未来": 0,
                   "墨清弦": 0,
                   "徵羽摩柯": 0
                   }
    for i in range(len(woclist)):
        for j in woclist[i].getSingers():
            singercount[j] += 1
    counts["woclist"] = singercount

    singercount = {"洛天依": 0,  # 0b10
                   "乐正绫": 0,  # 0b100
                   "言和": 0,  # 0b1000
                   "心华": 0,  # 0b10000
                   "星尘": 0,  # 0b100000
                   "乐正龙牙": 0,  # 0b1000000
                   "初音未来": 0,
                   "墨清弦": 0,
                   "徵羽摩柯": 0
                   }
    for i in range(len(pickuplist)):
        for j in pickuplist[i].getSingers():
            singercount[j] += 1
    counts["pickuplist"] = singercount

    return counts

if __name__ == "__main__":
    print("初始化....")
    parser = vsingersparser()
    mode = input("请选择输入模式 a:手动输入 b:文本导入-")
    otpt = input("是否将结果导出为文件(y/n)(default:n)")
    if otpt == "y":
        otpt = True
    else:
        otpt = False
    if mode == "a":
        print("选择模式: 手动输入\n")
        print("开始获取信息，请等待...")
        data = rank_b()
    elif mode == "b":
        print("选择模式:文本导入\n")
        if os.path.exists("input.txt"):
            print("模板文件已存在")
        else:
            print("正在生成模板")
            generateinputtxt()
            print("模板生成完成，请在本程序目录下找到input.txt打开并填写")
        temp = input("输入完成后请按回车。")
        try:
            print("开始获取信息，请等待...")
            data = rank_c(os.path.join("input.txt"),parser)
        except:
            print("导入文件时出错")
            sys.exit()
    else:
        print("没有这个模式")
        sys.exit()
    if otpt:
        print("导出结果中...")
        txtoutput(data)
        print("完成，导出为本目录下的output.txt")
    else:
        pass
    temp = input("程序已完成，回车结束程序")
    sys.exit()