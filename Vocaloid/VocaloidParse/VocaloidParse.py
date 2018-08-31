# -*- coding:utf-8 -*-

from functools import reduce
import re,requests,json

class vocaloidparser(object):
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

    def getkey(self, singerlist):
        return str(reduce(lambda x, y: x + y, map(lambda singer: self.__vsingerdict[singer], singerlist)))

    def combinesingers(self, used, notused):
        if len(notused) < 1:
            return
        newnotused = notused.copy()
        for singer in notused:
            newused = used.copy()
            newused.append(singer)
            newnotused.remove(singer)
            self.__vsingersdict[self.getkey(newused)] = newused
            self.combinesingers(newused, newnotused)

    def getSingersByTitleParser(self, title):
        singerskey = 0
        if title == None:
            title = ""
        for singer in self.__vsingerdict.keys():
            if singer in title:
                if singerskey & (1 << (str(bin(self.__vsingerdict[singer])).count('0') - 1)):
                    continue
                singerskey += self.__vsingerdict[singer]

        if singerskey == 0:
            return []
        else:
            return self.__vsingersdict[str(singerskey)]

    def getSingersByTags(self, tags):
        tags = list(tags)
        singerskey = 0
        for tag in tags:
            if tag in self.__vsingerdict.keys():
                if singerskey & (1 << (str(bin(self.__vsingerdict[tag])).count('0') - 1)):
                    continue
                singerskey += self.__vsingerdict[tag]
        if singerskey == 0:
            return []
        else:
            return self.__vsingersdict[str(singerskey)]

    def getParsedTitleByFind(self, title):
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

    def getParsedTitleByRe(self, title):

        parsedtitle = re.sub(r"【[\s\S]+?】","",title)

        if len(parsedtitle) == 0:
            return title
        else:
            return parsedtitle

    def getOutputFilename(self, title,singers,album):
        return "---".join([title, "、".join(singers), album])

    def ReqTags(self,aid):
        url = "https://api.bilibili.com/x/tag/archive/tags?aid=%s" % aid
        wb_data = requests.get(url)
        data = json.loads(wb_data.text)
        tags = []
        for item in data["data"]:
            tags.append(item["tag_name"])
        return tags