import requests, re
import json, time, sys, os
from functools import reduce
from VocaloidParse import vocaloidparser


class rankitem(object):
    def __init__(self, aid, title, parsedtitle, singers, author):
        self.title = title
        self.aid = aid
        self.parsedtitle = parsedtitle
        self.singers = singers
        self.author = author

    @classmethod
    def initFromitem(cls, item, parser):
        title = item["title"]
        aid = item["avid"]
        parsedtitle = parser.getParsedTitleByRe(title)
        title1, author, tags = cls.reqInfo(aid)
        singers = parser.getSingersByTitleParser(title)
        if len(singers) == 0:
            singers = parser.getSingersByTags(tags.split(","))
        return cls(aid, title, parsedtitle, singers, author)

    @classmethod
    def initFromAid(cls, aid, parser):
        title, author, tags = cls.reqInfo(aid)
        if title is None:
            return None
        parsedtitle = parser.getParsedTitleByRe(title)
        singers = parser.getSingersByTitleParser(title)
        if len(singers) == 0:
            singers = parser.getSingersByTags(tags.split(","))
        return cls(aid, title, parsedtitle, singers, author)

    @classmethod
    def reqInfo(cls, aid):
        url = "https://api.bilibili.com/x/web-interface/search/all?keyword=av%s" % aid
        wb_data = requests.get(url)
        data = json.loads(wb_data.text)
        if len(data["data"]["result"]["video"]) == 0:
            return ("", "", "")
        else:
            rs = data["data"]["result"]["video"][0]
            return (rs["title"], rs["author"], rs["tag"])

class videoitem(object):
    def __init__(self, aid, title, author):
        self.title = title
        self.aid = aid
        self.author = author

    @classmethod
    def initFromAid(cls, aid):
        title,author = cls.reqInfo(aid)
        return cls(aid,title,author)

    @classmethod
    def reqInfo(cls, aid):
        url = "https://api.bilibili.com/x/web-interface/search/all?keyword=av%s" % aid
        wb_data = requests.get(url)
        data = json.loads(wb_data.text)
        if len(data["data"]["result"]["video"]) == 0:
            return ("", "")
        else:
            rs = data["data"]["result"]["video"][0]
            return (rs["title"], rs["author"])



def getCount(items, parser):
    singercount = dict((vsinger, 0) for vsinger in parser.vsingerlist)
    for item in items:

        if not isinstance(item,rankitem):
            continue
        for singer in item.singers:
            singercount[singer] += 1

    return singercount


def fileFormatPrint(f, prefix, title, singers, author, aid):
    f.write("%s:【%s】 %s （UP:%s） av%s\n" % (prefix, ",".join(singers), title, author, aid))


def fileFormatPrintCount(f, singercount):
    for key, value in singercount.items():
        if value > 0:
            f.write("【%s】: %s " % (key, value))
    f.write("\n")


class unlimitVideo(object):
    def __init__(self):

        self.videos = []
        self.text = {}

    def gntInput(self, filedir="input.txt"):
        with open(filedir, "w", encoding="utf-8") as f:
            f.write("*---------------------------------------------------------*\n")
            f.write("***使用指南***\n")
            f.write("*每一行一个av号，不用加av 如 28922961*\n")
            f.write("*在 - 之后的所有内容按原样保存*\n")
            f.write("*---------------------------------------------------------*\n")
            f.write("***从下一行开始填写***\n")
            f.write("\n")
            f.write("*---------------------------------------------------------*\n")

    def loadInput(self, filedir="input.txt"):
        linenum = 0
        with open(filedir, "r", encoding="utf-8") as f:
            for line in f.readlines():
                l = line.strip()
                if len(l) == 0:
                    continue
                if l[0] == "-":
                    self.text[str(linenum)] = l[1:]
                    linenum += 1
                    continue
                if not l.isdigit():
                    continue
                self.videos.append(videoitem.initFromAid(l))
                linenum += 1
                time.sleep(0.1)

    def gntOutput(self, filedir="output.txt"):
        linenum = 0
        with open(filedir, "w", encoding="utf-8") as f:
            f.write("输出:\n")
            f.write("---------------------------------------------------------\n")
            for index,item in enumerate(self.videos): # type: videoitem
                text = self.text.get(str(linenum))
                if text != None:
                    f.write("%s\n" % text)
                    linenum +=1
                f.write("%s  (UP:%s)  av%s\n" %(item.title,item.author,item.aid))
                linenum +=1
            f.write("---------------------------------------------------------\n")

class unlimitVocaloid(object):
    def __init__(self, parser):

        self.parser = parser
        self.videos = []
        self.text = {}

    def gntInput(self, filedir="input.txt"):
        with open(filedir, "w", encoding="utf-8") as f:
            f.write("*---------------------------------------------------------*\n")
            f.write("***使用指南***\n")
            f.write("*每一行一个av号，不用加av 如 28922961*\n")
            f.write("*在 - 之后的所有内容按原样保存*\n")
            f.write("*---------------------------------------------------------*\n")
            f.write("***从下一行开始填写***\n")
            f.write("*---------------------------------------------------------*\n")

    def loadInput(self, filedir="input.txt"):
        linenum = 0
        with open(filedir, "r", encoding="utf-8") as f:
            for line in f.readlines():
                l = line.strip()
                if len(l) == 0:
                    continue
                if l[0] == "-":
                    self.text[str(linenum)] = l[1:]
                    linenum += 1
                    continue
                if not l.isdigit():
                    continue
                self.videos.append(rankitem.initFromAid(l, self.parser))
                linenum += 1
                time.sleep(0.1)

    def gntOutput(self, filedir="output.txt", count=True):
        linenum = 0
        with open(filedir, "w", encoding="utf-8") as f:
            f.write("输出:\n")
            f.write("---------------------------------------------------------\n")
            for index,item in enumerate(self.videos): # type: rankitem
                text = self.text.get(str(linenum))
                if text != None:
                    f.write("%s\n" % text)
                    linenum +=1
                fileFormatPrint(f,index,item.parsedtitle,item.singers,item.author,item.aid)
                linenum +=1
            f.write("---------------------------------------------------------\n")
            if count:
                fileFormatPrintCount(f, getCount(self.videos, self.parser))

class zkVocaloid(object):
    def __init__(self, parser):

        self.parser = parser
        self.zb = dict((index, None) for index in range(1, 31))
        self.woc = dict((index, None) for index in range(1, 6))
        self.pickup = []
        self.superhit = []
        self.op = None
        self.ed = None

    def gntInput(self, filedir="input.txt"):
        with open(filedir, "w", encoding="utf-8") as exfile:
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
            exfile.write("ed=\n")
            exfile.write("---------------------------------------------------------\n")

    def loadInput(self, filedir="input.txt"):
        with open(filedir, "r", encoding="utf-8") as f:
            for line in f.readlines():
                l = line.strip().split("=")
                if ((l[0].split("_")[0]) == "zb") and (len(l[1]) != 0):
                    if self.zb.get(l[0].split("_")[1]) == None:
                        continue
                    self.zb[l[0].split("_")[1]] = rankitem.initFromAid(l[1], self.parser)
                elif (l[0].split("_")[0] == "woc") and (len(l[1]) != 0):
                    if self.woc.get(l[0].split("_")[1]) == None:
                        continue
                    self.woc[l[0].split("_")[1]] = rankitem.initFromAid(l[1], self.parser)
                elif (l[0] == "pickup") and (len(l[1]) != 0):
                    self.pickup.append(rankitem.initFromAid(l[1], self.parser))
                elif (l[0] == "superhit") and (len(l[1]) != 0):
                    self.pickup.append(rankitem.initFromAid(l[1], self.parser))
                elif (l[0] == "op") and (len(l[1]) != 0):
                    self.op = rankitem.initFromAid(l[1], self.parser)
                elif (l[0] == "ed") and (len(l[1]) != 0):
                    self.ed = rankitem.initFromAid(l[1], self.parser)
                else:
                    pass
                time.sleep(0.1)

    def gntOutput(self, filedir="output.txt", count=True):
        with open(filedir, "w", encoding="utf-8") as f:
            f.write("抄榜结果:\n")
            f.write("---------------------------------------------------------\n")

            if self.op != None:
                fileFormatPrint(f, "op", self.op.parsedtitle, self.op.singers, self.op.author, self.op.aid)
            f.write("\n---------------------------------------------------------\n")

            f.write("主榜\n")
            for index in range(30, 0, -1):
                item = self.zb[str(index)]  # type:rankitem
                if item != None:
                    fileFormatPrint(f, "主榜%s" % index, item.parsedtitle, item.singers, item.author, item.aid)
            f.write("\n")
            if count:
                fileFormatPrintCount(f, getCount(self.zb.values(), self.parser))
            f.write("---------------------------------------------------------\n")

            f.write("SuperHits\n")
            for index, item in enumerate(self.superhit, start=1):  # type:rankitem
                fileFormatPrint(f, "SuperHits" % index, item.parsedtitle, item.singers, item.author, item.aid)
            f.write("\n")
            if count:
                fileFormatPrintCount(f, getCount(self.superhit, self.parser))
            f.write("---------------------------------------------------------\n")

            f.write("新曲推荐\n")
            for index, item in enumerate(self.pickup, start=1):  # type:rankitem
                fileFormatPrint(f, "PickUp" % index, item.parsedtitle, item.singers, item.author, item.aid)
            f.write("\n")
            if count:
                fileFormatPrintCount(f, getCount(self.pickup, self.parser))
            f.write("---------------------------------------------------------\n")

            f.write("woc一年了\n")
            for index in range(5, 0, -1):
                item = self.woc[str(index)]  # type:rankitem
                if item != None:
                    fileFormatPrint(f, "Woc%s" % index, item.parsedtitle, item.singers, item.author, item.aid)
            f.write("\n")
            if count:
                fileFormatPrintCount(f, getCount(self.woc.values(), self.parser))
            f.write("---------------------------------------------------------\n")

            if self.ed != None:
                fileFormatPrint(f, "op", self.ed.parsedtitle, self.ed.singers, self.ed.author, self.ed.aid)
            f.write("\n---------------------------------------------------------\n")


if __name__ == "__main__":
    parser = vocaloidparser()
    #mode = unlimitVideo(parser)
    mode = unlimitVideo()
    mode.gntInput()
    a = input("回车继续")
    mode.loadInput()
    mode.gntOutput()